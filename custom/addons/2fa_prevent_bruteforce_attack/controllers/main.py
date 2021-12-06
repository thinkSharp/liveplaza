# -*- coding: utf-8 -*-
import logging

from odoo.addons.web.controllers.main import ensure_db
from passlib.context import CryptContext
import socket
import odoo
from odoo import http, _
from odoo.http import request
from datetime import datetime

default_crypt_context = CryptContext(
    ['pbkdf2_sha512', 'md5_crypt'],
    deprecated=['md5_crypt'],
)

_logger = logging.getLogger(__name__)


class WebHome(odoo.addons.web.controllers.main.Home):

    @http.route('/web/error', type='http', auth="none")
    def error_login(self, mod=None, **kwargs):
        return request.render('auth_2FA.notify_error_login')

    # Override by misterling
    @http.route('/web/login', type='http', auth="none", sitemap=False)
    def web_login(self, redirect=None, **kw):
        ensure_db()
        request.params['login_success'] = False
        if request.httprequest.method == 'GET' and redirect and request.session.uid:
            return http.redirect_with_hash(redirect)

        if not request.uid:
            request.uid = odoo.SUPERUSER_ID

        values = request.params.copy()
        try:
            values['databases'] = http.db_list()
        except odoo.exceptions.AccessDenied:
            values['databases'] = None

        if request.httprequest.method == 'POST':
            # client_ip = request.httprequest.headers.environ.get('HTTP_X_REAL_IP') if request.httprequest.headers.environ.get('HTTP_X_REAL_IP') else False
            client_ip = request.httprequest.remote_addr
            # tìm check trong backlist IP đó đã bị ban chưa, ban rồi thì redirect sang site lỗi
            if client_ip:
                white_ip = request.env['white.list.ip'].sudo().search([('ip', '=', client_ip)])
                if not white_ip:
                    ip_address_client = request.env['check.login.fail'].search([('ip_address', '=', client_ip), ('state', '=', 'ban')])
                    if ip_address_client:
                        request.params['login_success'] = False
                        return request.redirect('/web/error')
            old_uid = request.uid
            try:
                request.env.cr.execute(
                    '''
                        SELECT id,
                               COALESCE(company_id, NULL), 
                               COALESCE(password, ''),
                               COALESCE(otp_first_use,FALSE,TRUE) 
                        FROM res_users 
                        WHERE login=%s
                    ''',
                    [request.params['login']]
                )
                res = request.env.cr.fetchone()
                # Kiểm tra nếu chưa tích bỏ mã QR trong profile thì yeu cầu check mã QR
                if not res:
                    raise odoo.exceptions.AccessDenied(_('Wrong login account'))
                [user_id, company_id, hashed, otp_first_use] = res

                if company_id and request.env['res.company'].browse(company_id).sudo().is_open_2fa:
                    # 验证密码正确性
                    valid, replacement = default_crypt_context.verify_and_update(request.params['password'], hashed)
                    if replacement is not None:
                        self._set_encrypted_password(self.env.user.id, replacement)
                    if valid:

                        # check if user use opt or not

                        if not request.env['res.users'].sudo().browse(user_id).otp_enable:
                            uid = request.session.authenticate(request.session.db, request.params['login'],
                                                               request.params['password'])

                            request.params['login_success'] = True
                            return http.redirect_with_hash(self._login_redirect(uid, redirect=redirect))
                        # end check if user use opt or not
                        if otp_first_use:
                            values['QRCode'] = 'data:image/png;base64,' + request.env['res.users'].browse(
                                user_id).otp_qrcode.decode('ascii')
                            values['otp_secret'] = request.env['res.users'].browse(
                                user_id).otp_secret
                            values['text'] = _(
                                'You are the first time to use OTP, please scan the QRCode to get validation code.you '
                                'should store this QRCode image and take good care of it! ')
                        response = request.render('auth_2FA.2fa_auth', values)
                        response.headers['X-Frame-Options'] = 'DENY'
                        return response
                    else:
                        raise odoo.exceptions.AccessDenied()
                # 没有打开双因子验证
                uid = request.session.authenticate(request.session.db, request.params['login'],
                                                   request.params['password'])
                request.params['login_success'] = True
                if client_ip:
                    old_check_login_detail = request.env['check.login.fail'].sudo().search(
                        [('ip_address', '=', client_ip), ('name', '=', values['login'])], limit=1)
                    if old_check_login_detail:
                        old_check_login_detail.sudo().write({
                            'state': 'active',
                            'count': 0
                        })
                return http.redirect_with_hash(self._login_redirect(uid, redirect=redirect))
            except odoo.exceptions.AccessDenied as e:
                request.uid = old_uid
                # Nếu login fail thì log lại , count +1, if count >10 thì ban lại
                if client_ip:
                    old_check_login_detail = request.env['check.login.fail'].sudo().search(
                        [('ip_address', '=', client_ip), ('name', '=', values['login'])], limit=1)
                    if old_check_login_detail:
                        if old_check_login_detail.state == 'ban':
                            request.params['login_success'] = False
                            return request.redirect('/web/error')
                        if old_check_login_detail.count >= 10:
                            old_check_login_detail.sudo().update({
                                'count': old_check_login_detail.count + 1,
                                'state': 'ban',
                            })
                            request.env['log.time.login'].sudo().create({
                                'time': datetime.now(),
                                'note': 'Fail Login',
                                'check_login_fail_id': old_check_login_detail.id
                            })
                        else:
                            old_check_login_detail.sudo().update({
                                'count': old_check_login_detail.count + 1,
                                'state': 'active'
                            })
                            request.env['log.time.login'].sudo().create({
                                'time': datetime.now(),
                                'note': 'Fail Login',
                                'check_login_fail_id': old_check_login_detail.id
                            })
                    else:
                        login_fail = request.env['check.login.fail'].sudo().create({
                            'name': values['login'],
                            'ip_address': client_ip,
                            'count': 1,
                            'state': 'active'
                        })
                        request.env['log.time.login'].sudo().create({
                            'time': datetime.now(),
                            'note': 'Fail Login',
                            'check_login_fail_id': login_fail.id
                        })
                if e.args == odoo.exceptions.AccessDenied().args:
                    values['error'] = _("Wrong login/password")
                else:
                    values['error'] = e.args[0]
        else:
            if 'error' in request.params and request.params.get('error') == 'access':
                values['error'] = _('Only employee can access this database. Please contact the administrator.')

        if 'login' not in values and request.session.get('auth_login'):
            values['login'] = request.session.get('auth_login')

        if not odoo.tools.config['list_db']:
            values['disable_database_manager'] = True

        # otherwise no real way to test debug mode in template as ?debug =>
        # values['debug'] = '' but that's also the fallback value when
        # missing variables in qweb
        if 'debug' in values:
            values['debug'] = True

        response = request.render('web.login', values)
        response.headers['X-Frame-Options'] = 'DENY'
        return response

    @http.route('/web/login/2fa_auth', type='http', auth="none", website=True)
    def web_login_2fa_auth(self, redirect=None, **kw):
        ensure_db()
        request.params['login_success'] = False
        # client_ip = request.httprequest.headers.environ.get('HTTP_X_REAL_IP') if request.httprequest.headers.environ.get('HTTP_X_REAL_IP') else False
        client_ip = request.httprequest.remote_addr
        if not request.uid:
            request.uid = odoo.SUPERUSER_ID

        values = request.params.copy()
        try:
            values['databases'] = http.db_list()
        except odoo.exceptions.AccessDenied:
            values['databases'] = None
        old_uid = request.uid
        try:
            uid = request.session.authenticate(request.session.db, request.params['login'],
                                               request.params['password'])
            request.params['login_success'] = True
            request.env['res.users'].sudo().browse(uid).otp_first_use = False
            if client_ip:
                old_check_login_detail = request.env['check.login.fail'].sudo().search(
                    [('ip_address', '=', client_ip), ('name', '=', values['login'])], limit=1)
                if old_check_login_detail:
                    old_check_login_detail.sudo().write({
                        'state': 'active',
                        'count': 0
                    })
            return http.redirect_with_hash(self._login_redirect(uid, redirect=redirect))
        except odoo.exceptions.AccessDenied as e:
            request.uid = old_uid
            if client_ip:
                old_check_login_detail = request.env['check.login.fail'].sudo().search(
                    [('ip_address', '=', client_ip), ('name', '=', values['login'])], limit=1)
                if old_check_login_detail:
                    if old_check_login_detail.state == 'ban':
                        request.params['login_success'] = False
                        return request.redirect('/web/error')
                    if old_check_login_detail.count >= 10:
                        old_check_login_detail.sudo().update({
                            'count': old_check_login_detail.count + 1,
                            'state': 'ban',
                        })
                        request.env['log.time.login'].sudo().create({
                            'time': datetime.now(),
                            'note': 'Fail Login',
                            'check_login_fail_id': old_check_login_detail.id
                        })
                    else:
                        old_check_login_detail.sudo().update({
                            'count': old_check_login_detail.count + 1,
                            'state': 'active'
                        })
                        request.env['log.time.login'].sudo().create({
                            'time': datetime.now(),
                            'note': 'Fail Login',
                            'check_login_fail_id': old_check_login_detail.id
                        })
                else:
                    login_fail = request.env['check.login.fail'].sudo().create({
                        'name': values['login'],
                        'ip_address': client_ip,
                        'count': 1,
                        'state': 'active'
                    })
                    request.env['log.time.login'].sudo().create({
                        'time': datetime.now(),
                        'note': 'Fail Login',
                        'check_login_fail_id': login_fail.id
                    })
            if e.args == odoo.exceptions.AccessDenied().args:
                values['error'] = _("Wrong login/password")
            else:
                values['error'] = e.args[0]
        if not odoo.tools.config['list_db']:
            values['disable_database_manager'] = True

        if 'login' not in values and request.session.get('auth_login'):
            values['login'] = request.session.get('auth_login')

        if 'debug' in values:
            values['debug'] = True
        response = request.render('auth_2FA.2fa_auth', values)
        response.headers['X-Frame-Options'] = 'DENY'
        return response

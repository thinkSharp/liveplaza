# -*- coding: utf-8 -*-
import base64
import io
import logging
import pyotp
import pyqrcode

from odoo import models, fields, api, _
from odoo.exceptions import AccessDenied
from odoo.http import request

_logger = logging.getLogger(__name__)


class ResUsers(models.Model):
    _inherit = 'res.users'

    otp_enable = fields.Boolean(string="Is OTP Used", default=False)
    otp_first_use = fields.Boolean(string="First Use OTP", default=True)
    otp_type = fields.Selection(selection=[('time', _('Time based')), ('count', _('Counter based'))], default='time',
                                string="Type",
                                help="Type of 2FA, time = new code for each period, counter = new code for each login")
    otp_secret = fields.Char(string="Secret", size=16, help='16 character base32 secret',
                             default=lambda self: pyotp.random_base32())
    otp_counter = fields.Integer(string="Counter", default=0)
    otp_digits = fields.Integer(string="Digits", default=6, help="Length of the code")
    otp_period = fields.Integer(string="Period", default=30, help="Seconds to update code")
    otp_qrcode = fields.Binary(compute="_compute_otp_qrcode")

    otp_uri = fields.Char(compute='_compute_otp_uri', string="URI")

    @classmethod
    def authenticate(cls, db, login, password, user_agent_env):
        client_ip = request.httprequest.headers.environ.get('HTTP_X_REAL_IP') if request.httprequest.headers.environ.get('HTTP_X_REAL_IP') else False
        # tìm check trong backlist IP đó đã bị ban chưa
        if client_ip:
            ip_address_client = request.env['check.login.fail'].search([('name', '=', login), ('state', '=', 'ban')])
            if ip_address_client:
                raise AccessDenied()
        if user_agent_env:
            cls.user_agent_env = user_agent_env
        try:
            res = super(ResUsers, cls).authenticate(db, login, password, user_agent_env)
            old_check_login_detail = request.env['check.login.fail'].sudo().search(
                [('ip_address', '=', client_ip), ('name', '=', login)], limit=1)
            if old_check_login_detail:
                old_check_login_detail.sudo().write({
                    'state': 'active',
                    'count': 0
                })
            return res
        except:
            if client_ip:
                old_check_login_detail = request.env['check.login.fail'].sudo().search(
                    [('ip_address', '=', client_ip), ('name', '=', login)], limit=1)
                if old_check_login_detail:
                    if old_check_login_detail.state == 'ban':
                        request.params['login_success'] = False
                        # return request.redirect('/web/error')
                    if old_check_login_detail.count >= 2:
                        old_check_login_detail.sudo().update({
                            'count': old_check_login_detail.count + 1,
                            'state': 'ban',
                        })
                    else:
                        old_check_login_detail.sudo().update({
                            'count': old_check_login_detail.count + 1,
                            'state': 'active'
                        })
                else:
                    request.env['check.login.fail'].sudo().create({
                        'name': login,
                        'ip_address': client_ip,
                        'count': 1,
                        'state': 'active'
                    })
            return super(ResUsers, cls).authenticate(db, login, password, user_agent_env)
        # return res

    def toggle_otp_first_use(self):
        for record in self:
            record.otp_first_use = not record.otp_first_use

    @api.model
    def create_qr_code(self, uri):
        buffer = io.BytesIO()
        qr = pyqrcode.create(uri)
        qr.png(buffer, scale=3)
        return base64.b64encode(buffer.getvalue()).decode()

    @api.depends('otp_uri')
    def _compute_otp_qrcode(self):
        for record in self:
            record.otp_qrcode = record.create_qr_code(record.otp_uri)

    @api.depends('otp_type', 'otp_period', 'otp_digits', 'otp_secret', 'company_id', 'otp_counter')
    def _compute_otp_uri(self):
        for record in self:
            if record.otp_type == 'time':
                record.otp_uri = pyotp.utils.build_uri(secret=record.otp_secret, name=record.login,
                                                       period=record.otp_period)
            else:
                record.otp_uri = pyotp.utils.build_uri(secret=record.otp_secret, name=record.login,
                                                       initial_count=record.otp_counter,
                                                       digits=record.otp_digits)
    @api.model
    def check_otp(self, otp_code):
        res_user = self.sudo().env['res.users'].browse(self.env.uid)
        if res_user.otp_type == 'time':
            totp = pyotp.TOTP(res_user.otp_secret)
            return totp.verify(otp_code)
        elif res_user.otp_type == 'count':
            hotp = pyotp.HOTP(res_user.otp_secret)
            for count in range(res_user.otp_counter, res_user.otp_counter + 20):
                if count > 0 and hotp.verify(otp_code, count):
                    res_user.sudo().write({
                        'otp_counter': count + 1
                    })
                    return True
        return False

    def _check_credentials(self, password):
        super(ResUsers, self)._check_credentials(password)
        if not request.params.get('login_by_mobile'):
            if request.params.get('tfa_code'):
                if self.otp_enable and self.company_id.is_open_2fa and not self.check_otp(
                        request.params.get('tfa_code')):
                    raise AccessDenied(_('Validation Code Error!'))
            else:
                if hasattr(self, 'user_agent_env'):
                    if self.otp_enable and self.company_id.is_open_2fa and not self.check_otp(
                            self.user_agent_env.get('tfa_code')):
                        raise AccessDenied(_('Validation Code Error!'))

    def generate_new_otp_secret(self):
        for rec in self:
            rec.otp_secret = pyotp.random_base32()

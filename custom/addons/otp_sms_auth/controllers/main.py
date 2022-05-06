# -*- coding: utf-8 -*-
#################################################################################
#
#   Copyright (c) 2015-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>)
#   See LICENSE file for full copyright and licensing details.
#   If not, see <https://store.webkul.com/license.html/>
#
#################################################################################

from odoo import http, tools, api, _
from odoo.http import request
from odoo.addons.web.controllers.main import ensure_db, Home
from odoo.addons.otp_auth.controllers.main import AuthSignupHome
from odoo import http
from odoo.exceptions import UserError
import pyotp
import datetime as dt
import logging
_logger = logging.getLogger("******** OTP ********")


class AuthSignupHome(AuthSignupHome):

    def do_signup(self, qcontext):
        """ Shared helper that creates a res.partner out of a token """
        values = {key: qcontext.get(key) for key in (
            'login', 'name', 'password', 'mobile')}
        if not values:
            raise UserError(_("The form was not properly filled in."))
        if values.get('password') != qcontext.get('confirm_password'):
            raise UserError(_("Passwords do not match; please retype them."))
        supported_langs = [
            lang['code'] for lang in request.env['res.lang'].sudo().search_read([], ['code'])]
        if request.lang in supported_langs:
            values['lang'] = request.lang
        self._signup_with_values(qcontext.get('token'), values)
        request.env.cr.commit()

    @http.route(['/send/otp'], type='json', auth="public", methods=['POST'], website=True)
    def send_otp(self, **kwargs):
        otpdata = self.getOTPData()
        otp = otpdata[0]
        otp_time = otpdata[1]
        start = dt.datetime.now()
        kwargs['otpdata'] = otpdata
        res = None
        otp_notification_mode = request.env['ir.default'].sudo().get(
            'website.otp.settings', 'otp_notification_mode')
        # if kwargs.get('loginOTP'):
        # if otp_notification_mode == 'both':
        #     request.env['send.otp'].setDataSession(otpdata)
        if otp_notification_mode != 'sms':
            res = super(AuthSignupHome, self).send_otp(**kwargs)
        res = res if res else {}
        if otp_notification_mode != 'email':
            mobile = kwargs.get('mobile')
            login = kwargs.get('login')
            if login.isdigit():
                userObj = request.env["res.users"].sudo().search(
                    [("mobile", "=", mobile)])
                if userObj:
                    loginId = userObj.login
                    countryObj = userObj.sudo().partner_id.country_id
                    phone_code = countryObj.phone_code
                    response = request.env['send.otp'].sms_send_otp(
                        mobile, False, otp, phone_code)
                    errorSMS = response._context.get('sms_error')
                    end = dt.datetime.now()
                    rest = (end - start).total_seconds()
                    if rest < otp_time:
                        otp_time = int(otp_time - rest)
                    if errorSMS:
                        msg = "Failed to send OTP !! Please ensure that you have given correct Mobile No.<br/><center>or</center> <br/><p class='alert alert-danger'> Reason: {}</p>".format(
                            errorSMS)
                        res['mobile'] = {'status': 0, 'message': _(
                            msg), 'otp_time': 0, 'email': False}
                    else:
                        res['mobile'] = {'status': 1, 'message': _("OTP has been sent to given Mobile No. : {}.".format(
                            mobile)), 'otp_time': otp_time, 'email': loginId}
                else:
                    res['mobile'] = {'status': 0, 'message': _(
                        "Failed to send OTP !! Please ensure that you have given correct Mobile No."), 'otp_time': 0, 'email': False}
        if not kwargs.get('email') and res.get('email', {}).get('status') == 0:
            res['email'] = {'status': 0, 'message': _(
                "Failed to send OTP !! Please ensure that you have given correct email ID."), 'otp_time': 0, 'email': False}
        return res

    @http.route(['/get/user/email'], type='json', auth="public", methods=['POST'], website=True)
    def get_user_email(self, **kwargs):
        mobile = kwargs.get('mobile')
        login = kwargs.get('login')
        resp = {}
        if not mobile and login:
            userObj = request.env["res.users"].sudo().search(
                [("login", "=", login)], limit=1)
            mobile = userObj.mobile if userObj else False
        elif mobile and not login:
            userObj = request.env["res.users"].sudo().search(
                [("mobile", "=", mobile)], limit=1)
            login = userObj.login if userObj else False

        if login and mobile:
            resp = {'status': 1, 'message': _("Mobile No. : {}.".format(
                mobile)), 'mobile': mobile, 'login': login}
        elif not login and mobile:
            resp = {'status': 0, 'message': _(
                "Failed to login !! Please ensure that you have given correct Mobile No."), 'mobile': mobile, 'login': False}
        elif not mobile and login:
            resp = {'status': 0, 'message': _(
                "Failed to login !! Please ensure that you have given correct login ID."), 'mobile': False, 'login': login}
        else:
            resp = {'status': 0, 'message': _(
                "Failed to login !! Please enter a mobile no./login ID"), 'mobile': False, 'login': False}
        return resp

    @http.route(['/generate/otp'], type='json', auth="public", methods=['POST'], website=True)
    def generate_otp(self, **kwargs):
        mobile = kwargs.get('mobile')
        email = kwargs.get('email')
        if not mobile:
            return [0, _("Please enter a mobile number"), 0]
        else:
            if not mobile.isdigit():
                return [0, _("Please enter a valid mobile number"), 0]

        res = super(AuthSignupHome, self).generate_otp(**kwargs)
        otp_notification_mode = request.env['ir.default'].sudo().get(
            'website.otp.settings', 'otp_notification_mode')
        if otp_notification_mode != 'email':
            if mobile and res:
                if otp_notification_mode == 'both':
                    if email.isdigit():
                        res[1] = "OTP has been sent to given Mobile No: {}".format(
                            mobile)
                        res[0] = 1
                    else:
                        res[1] = "{}" .format(res[1])
                    # res[1] = "{} and Mobile No: {}".format(res[1], mobile)
                elif otp_notification_mode == 'sms':
                    res[1] = "OTP has been sent to given Mobile No: {}".format(
                        mobile)
                    res[0] = 1
        return res

    def checkExistingUser(self, **kwargs):
        message = False
        otp_notification_mode = request.env['ir.default'].sudo().get(
            'website.otp.settings', 'otp_notification_mode')
        if otp_notification_mode != 'sms':
            message = super(AuthSignupHome, self).checkExistingUser(**kwargs)
        mobile = kwargs.get('mobile')
        userObj = request.env["res.users"].sudo().search(
            [("mobile", "=", mobile)])
        if userObj and mobile:
            message = [
                0, _("Another user is already registered using this mobile no."), 0]
        if not message:
            message = [
                0, _("OTP can't send because email OTP notification is not enabled."), 0]
        return message

    def sendOTP(self, otp, **kwargs):
        res = super(AuthSignupHome, self).sendOTP(otp, **kwargs)
        email = kwargs.get('email')
        userName = kwargs.get('userName')
        mobile = kwargs.get('mobile')
        country = kwargs.get('country')
        phone_code = False
        if country:
            country = int(country)
            countryObj = request.env['res.country'].sudo().browse(country)
            phone_code = countryObj.phone_code

        if email.isdigit():
            request.env['send.otp'].sms_send_otp(
                mobile, userName, otp, phone_code)

        return res

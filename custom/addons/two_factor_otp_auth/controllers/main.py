# Copyright 2020 VentorTech OU
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl-3.0).

from odoo import http, _
from odoo.addons.web.controllers.main import Home
from odoo.http import Controller, request, route

from ..exceptions import MissingOtpError, InvalidOtpError


from ..lib.otp import OTP
from ..lib.qr import QRCode


class Login2fa(Home):

    @http.route()
    def web_login(self, redirect=None, **kw):
        """
        Overload core method to start Second Factor validation step
        """
        try:
            response = super(Login2fa, self).web_login(redirect, **kw)
        except MissingOtpError:
            # user will get into this block if login process is not fully successful
            # For example, when first login was successful, but 2FA token is missing
            # So we can start second authentication step (OTP)
            response = self._redirect_to_2fa()
        except InvalidOtpError:
            message = _("Your security code is wrong")
            response = self._redirect_to_2fa(message)
        else:
            params = request.params
            if params.get("login_success"):
                user = request.env.user
                if user and user.enable_2fa and not user.secret_code_2fa:
                    # If credentials are Okay, but a user doesn't have
                    # QR code, that mean it's first success login with
                    # one-time-password. Now QR Code with it's Secret
                    # Code can be saved into the user.
                    values = {
                        "secret_code_2fa": params.get("secret_code_2fa"),
                    }
                    user.sudo().write(values)

        return response

    @staticmethod
    def _redirect_to_2fa(message=None):
        """
        Method to get response object that depends on user and request params values
        argument:
         *message(str) - error message
        Returns:
         *response object
        """
        values = request.params.copy()
        if message:
            values.update({
                "error": message,
            })
        user_id = request.session.otk_uid
        user = request.env["res.users"].sudo().browse(user_id)

        if user.secret_code_2fa or values.get("qr_code_2fa") or values.get("error"):
            template = "two_factor_otp_auth.2fa_verify_login"

        else:
            template = "two_factor_otp_auth.scan_code"

            secret_code, qr_code = user._generate_secrets()
            values.update({
                "qr_code_2fa": qr_code,
                "secret_code_2fa": secret_code,
            })

        return request.render(template, values)


class TwoFAPortal(Controller):

    @route('/my/disable_2fa', type="http", auth="user", website=True)
    def disable_2fa(self, **kw):
        code = request.params.get('otp_code')
        current_user = request.env.user

        if not current_user.enable_2fa:
            return request.redirect('/my/home')
        elif not code:
            return request.render("two_factor_otp_auth.2fa_disable")
        elif current_user.verify_2fa(code):
            current_user.do_disable_2fa()
            return request.redirect('/my/home')
        else:
            context = {
                'error': _("Your Security code is wrong.")
            }
            return request.render("two_factor_otp_auth.2fa_disable", context)


    @route('/my/change_2fa', type="http", auth="user", website=True)
    def change_2fa(self, **kw):
        params = request.params.copy()
        code = params.get('otp_code')
        user = request.env.user

        if not user.enable_2fa:
            return request.redirect('/my/enable_2fa')
        elif not code:
            return request.render("two_factor_otp_auth.2fa_verify_change")
        elif user.verify_2fa(code):
            otp = OTP.new()
            uri = otp.uri(name=user.login)
            qr_code = QRCode(uri)
            context = {
                "qr_code_2fa": qr_code.base64,
                "secret_code_2fa": otp.secret,
                "uri": uri,
                "old_secret_code": user.secret_code_2fa
            }
            return request.render("two_factor_otp_auth.2fa_change_setup", context)
        else:
            context = {
                'error': _("Your Security code is wrong.")
            }
            return request.render("two_factor_otp_auth.2fa_verify_change", context)


    @route('/my/enable_2fa', type="http", auth="user", website=True)
    def enable_2fa(self, **kw):
        params = request.params.copy()
        old_secret = params.get('old_secret_code')
        secret = params.get('secret_code_2fa')
        code = params.get('otp_code')
        user = request.env.user

        if user.enable_2fa and user.secret_code_2fa != old_secret:
            return request.redirect('/my/change_2fa')
        elif not secret or not code:
            otp = OTP.new()
            uri = otp.uri(name=user.login)
            qr_code = QRCode(uri)
            context = {
                "qr_code_2fa": qr_code.base64,
                "secret_code_2fa": otp.secret,
                "uri": uri,
            }
            return request.render("two_factor_otp_auth.2fa_setup", context)
        elif OTP(secret).verify(code):
            user.do_enable_2fa(secret)
            return request.redirect('/my/home')
        else:
            context = {}
            context.update(params)
            context.update({
                "qr_code_2fa": params.get('qr_code_2fa').encode()
            })
            context.update({
                'error': _("Your security code is wrong.")
            })
            return request.render("two_factor_otp_auth.2fa_setup", context)

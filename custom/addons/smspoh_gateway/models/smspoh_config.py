# -*- coding: utf-8 -*-
##########################################################################
# Author      : Webkul Software Pvt. Ltd. (<https://webkul.com/>)
# Copyright(c): 2017-Present Webkul Software Pvt. Ltd.
# All Rights Reserved.
#
#
#
# This program is copyright property of the author mentioned above.
# You can`t redistribute it and/or modify it.
#
#
# You should have received a copy of the License along with this program.
# If not, see <https://store.webkul.com/license.html/>
##########################################################################

import logging
from odoo import models, fields, api, _
from .smspoh_messaging import send_sms_using_smspoh
from odoo.exceptions import Warning

_logger = logging.getLogger(__name__)


class SmsMailServer(models.Model):
    """Configure the smspoh sms gateway."""

    _inherit = "sms.mail.server"
    _name = "sms.mail.server"
    _description = "smspoh Gateway"

    smspoh_api_key = fields.Char(string="API Key", help="API key associated with the Smspoh account.")
    smspoh_sender = fields.Char(string="Sender ID", help="Use this field to specify the sender name for your message. This must be at least 3 characters in length but no longer than 11 alphanumeric characters or 13 numeric characters.")


    def test_conn_smspoh(self):
        sms_body = "Smspoh Test Connection Successful........"
        mobile_number = self.user_mobile_no
        response = send_sms_using_smspoh(
            sms_body, mobile_number, sms_gateway=self, test=True)
        if response.get('status'):
            if self.sms_debug:
                _logger.info(
                    "===========Test Connection status has been sent on %r mobile number", mobile_number)
            raise Warning(
                "Test Connection status has been sent on %s mobile number" % mobile_number)
        else:
            if self.sms_debug:
                _logger.error(
                    "==========One of the information given by you is wrong. It may be [Mobile Number] or [API KEY]")
            raise Warning(
                "One of the information given by you is wrong. It may be [Mobile Number] or [API Key]")

    @api.model
    def get_reference_type(self):
        selection = super(SmsMailServer, self).get_reference_type()
        selection.append(('smspoh', 'Smspoh'))
        return selection

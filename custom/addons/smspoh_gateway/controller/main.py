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

from odoo.http import request
from odoo import http
_logger = logging.getLogger(__name__)


class SmspohNotify(http.Controller):
    @http.route(
        ['/smspoh/webhooks/delivery-receipt'], type='http', methods=['POST',"GET"], auth='public',
        website=True, csrf=False)
    def smspoh_notification(self, **post):
        """ smspoh notification controller"""
        # post ={'id': '1234567', 'status': 'Delivered', 'update_at': '1609941694'}
        _logger.info(
            "WEBKUL DEBUG FOR Smspoh: SUMMARY(POST DATA)%r", post)
        all_sms_report = request.env["sms.report"].sudo().search(
            [('state', 'in', ('sent', 'new'))])
        for sms in all_sms_report:
            if sms.nexmo_sms_id:
                sms_sms_obj = sms.sms_sms_id
                sms.status_hit_count += 1
                if post.get('id') == sms.smspoh_sms_id:
                    if post.get("status") == "Delivered":
                        if sms.auto_delete:
                            sms.sudo().unlink()
                            request._cr.commit()
                            if sms_sms_obj.auto_delete and \
                                    not sms_sms_obj.sms_report_ids:
                                sms_sms_obj.sudo().unlink()
                                request._cr.commit()
                            break
                        else:
                            sms.state = "delivered"
                            request._cr.commit()
                    if post.get('status') == 'Undelivered':
                        sms.state = "undelivered"
                        request._cr.commit()
        return "Sucessfully sms received!!!"

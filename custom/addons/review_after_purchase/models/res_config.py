# -*- coding: utf-8 -*-
#################################################################################
# Author      : Webkul Software Pvt. Ltd. (<https://webkul.com/>)
# Copyright(c): 2015-Present Webkul Software Pvt. Ltd.
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
#################################################################################
from odoo import api, fields, models

import logging
_logger = logging.getLogger(__name__)

class WebsiteSaleReviewSettings(models.Model):
    _name = 'website.sale.review.config.settings'
    _description ="review.config.settings"

    @api.model
    def _get_default_cron(self):
        ir_model_data = self.env['ir.model.data']
        cron_id = ir_model_data.get_object_reference('review_after_purchase', 'ir_cron_automatic_review')[1]
        return cron_id

    @api.model
    def _get_default_email_template(self):
        ir_model_data = self.env['ir.model.data']
        temp_id = ir_model_data.get_object_reference('review_after_purchase', 'review_after_purchase_mail')[1]
        return temp_id

    # is_active = fields.Boolean(string="Active on website")
    name = fields.Char(string="Name", required=True)
    enable_automatic_review = fields.Boolean(string='Enable automatic review feature')
    wk_cron_shedular = fields.Many2one('ir.cron', string='Cron Settings', readonly=True, default=_get_default_cron)
    days = fields.Integer(string="Day after", help="Number of days to sent Review mail after ordered date.", default=7)
    status = fields.Selection([('confirm','Confirmed'),('deliver','Delivered'),('invoice','Invoiced'),('deliver_invoice','Delivered and Invoiced')], string="Order Status", help="Send Review mail for which order status", default="confirm")
    wk_email_template = fields.Many2one('mail.template', string='Email Template', required=True, default = _get_default_email_template)

    @api.model
    def create_wizard(self):
        wizard_id = self.env['website.message.wizard'].create({'message':_("Currently a Configuration Setting for After Sale Review is active. You can not active other Configuration Setting. So, If you want to deactive the previous active configuration setting and active new configuration then click on 'Deactive Previous And Active New' button else click on 'cancel'.")})
        return {
            'name': _("Message"),
                'view_mode': 'form',
                'view_id': False,
                'res_model': 'website.message.wizard',
                'res_id': int(wizard_id.id),
                'type': 'ir.actions.act_window',
                'nodestroy': True,
                'target': 'new'
            }


    def toggle_is_active(self):
        """ Inverse the value of the field ``active`` on the records in ``self``. """
        
        active_ids = self.search([('enable_automatic_review', '=', True),('id', 'not in', [self.id])])
        for record in self:
            if active_ids:
                return self.create_wizard()
            record.enable_automatic_review = not record.enable_automatic_review

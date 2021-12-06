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
from datetime import datetime, timedelta, date
from odoo.addons.http_routing.models.ir_http import slug

import logging
_logger = logging.getLogger(__name__)

class SaleOrder(models.Model):

    _inherit = 'sale.order'

    review_sent = fields.Boolean(string="Sent Review Mail")

    def send_email_cron(self):
        config = self.env['website.sale.review.config.settings'].sudo().search([('enable_automatic_review','=',True)],limit=1)
        if config:
            order_date = date.today() - timedelta(days=config.days)
            order_date = fields.Date.to_string(order_date)
            domain=[('date_order','<=', order_date),('review_sent','=',False)]
            if config.status == 'deliver':
                orders = self.env['sale.order']
                for delivery in self.env['stock.picking'].sudo().search([]):
                    if delivery.state=='done' or delivery.state=='cancel':
                        orders += self.env['sale.order'].sudo().search(domain + [('name','=',delivery.origin)])
            elif config.status == 'invoice':
                orders = self.env['sale.order'].sudo().search(domain+[('invoice_status','=','invoiced')])
            elif config.status == 'confirm':
                orders = self.env['sale.order'].sudo().search(domain+[('state','=','sale')])
            elif config.status == 'deliver_invoice':
                orders = self.env['sale.order']
                for delivery in self.env['stock.picking'].sudo().search([]):
                    if delivery.state=='done' or delivery.state=='cancel':
                        orders += self.env['sale.order'].sudo().search(domain + [('name','=',delivery.origin),('invoice_status','=','invoiced')])

            for order in set(orders):
                config.wk_email_template.send_mail(order.id, True)
                order.review_sent = True
                self._cr.commit()
            return True
        else:
            _logger.info('================After Sale Review Configuration not set.')

    def get_base_url(self):
        return self.env['ir.config_parameter'].get_param('web.base.url')

    def product_url(self, product):
        return slug(product)

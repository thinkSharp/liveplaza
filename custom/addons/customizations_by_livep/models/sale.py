# -*- coding: utf-8 -*-

from odoo import api, fields, models, _

class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    seller_class_id = fields.Many2one('subscription.plan', 'Seller Class', ondelete='cascade')
    edd = fields.Datetime('Expected Delivery Date', readonly=True, compute='_get_edd')
    commission_amount = fields.Float('Commission', readonly=True, compute='_get_commission')

    def _get_edd(self):
        for record in self:
            record.edd = record.order_id.expected_date

    def _get_commission(self):
        for record in self:
            commission_rate = record.marketplace_seller_id.commission
            record.commission_amount = record.price_subtotal * commission_rate / 100
            

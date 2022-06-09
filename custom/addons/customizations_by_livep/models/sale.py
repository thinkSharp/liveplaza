# -*- coding: utf-8 -*- --

from odoo import api, fields, models, _

class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    seller_class_id = fields.Many2one('subscription.plan', 'Seller Class', ondelete='cascade')
    edd = fields.Datetime('Expected Delivery Date', readonly=True, compute='_get_edd')
    commission_amount = fields.Float('Commission', readonly=True, compute='_get_commission')
    selected_checkout = fields.Boolean(string='Selected For Checkout', defalut=False)


    def _get_edd(self):
        for record in self:
            record.edd = record.order_id.expected_date

    def _get_commission(self):
        for record in self:
            commission_rate = record.marketplace_seller_id.commission
            record.commission_amount = record.price_subtotal * commission_rate / 100

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    checked_amount_untaxed = fields.Monetary(string='Checked Untaxed Amount', store=True, readonly=True,
                                             compute='_checked_amount_all', tracking=5, default=0.0)
    checked_amount_tax = fields.Monetary(string='Checked Taxes', store=True, readonly=True, compute='_checked_amount_all',default=0.0)
    checked_amount_total = fields.Monetary(string='Checked Total', store=True, readonly=True, compute='_checked_amount_all', tracking=4)

    @api.depends('order_line.price_total')
    def _checked_amount_all(self):
        """
        Compute the total amounts of the SO.
        """
        for order in self:
            checked_amount_untaxed = checked_amount_tax = 0.0
            for line in order.order_line:
                print("!!!!!!!!!!!!! line = ", line)
                if line.selected_checkout == True:
                    print("True True True True True")
                    checked_amount_untaxed += line.price_subtotal
                    checked_amount_tax += line.price_tax
                else:
                    print("False False False False False")
            order.update({
                'checked_amount_untaxed': checked_amount_untaxed,
                'checked_amount_tax': checked_amount_tax,
                'checked_amount_total': checked_amount_untaxed + checked_amount_tax,
            })


            

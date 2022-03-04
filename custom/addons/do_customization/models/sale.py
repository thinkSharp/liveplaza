# -*- coding: utf-8 -*-
#################################################################################
# Author      : Webkul Software Pvt. Ltd. (<https://webkul.com/>)
# Copyright(c): 2015-Present Webkul Software Pvt. Ltd.
# License URL : https://store.webkul.com/license.html/
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
import dateutil
from datetime import datetime

from odoo import models, fields, api, _
from odoo.addons.website_sale_stock.models.sale_order import SaleOrder as WebsiteSaleStock
import logging
_logger = logging.getLogger(__name__)

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    payment_upload = fields.Binary(string='Upload Payment')
    payment_upload_name = fields.Char(string='Upload Payment')
    # state = fields.Selection([
    #         ('draft', 'Quotation'),
    #         ('sent', 'Quotation Sent'),
    #         ('sale', 'Sales Order'),
    #         ('approve_by_admin', 'Approved by Admin'),
    #         ('done', 'Locked'),
    #         ('cancel', 'Cancelled'),
    #         ], string='Status', readonly=True, copy=False, index=True, tracking=3, default='draft')

    # def action_confirm(self):
    #     self.ensure_one()
    #     res = super(SaleOrder, self).action_confirm()
    #     if self.get_portal_last_transaction().acquirer_id.provider == 'cash_on_delivery' and self.state == 'sale':
    #         self.action_admin()
    #
    #     return res
    
    # def action_admin(self):
    #     if self.filtered(lambda so: so.state != 'sale'):
    #         raise UserError(_('Only sale orders can be marked as sent directly.'))
    #     for order in self:
    #         order.message_subscribe(partner_ids=order.partner_id.ids)
    #     if self.write({'state': 'approve_by_admin'}):        
    #         picking_obj = self.env['stock.picking'].search([('origin','=',self.name)])
    #         picking_obj.write({'payment_provider': self.get_portal_last_transaction().acquirer_id.provider,
    #                            'is_admin_approved': True,
    #                            'hold_state': False})
    #
    #         if self.get_portal_last_transaction().acquirer_id.provider != 'cash_on_delivery':
    #             picking_obj.write({'payment_upload': self.payment_upload, 
    #                                'paid_amount': self.get_portal_last_transaction().amount, 
    #                                'payment_remark': self.get_portal_last_transaction().reference,
    #                                'journal_id': self.get_portal_last_transaction().acquirer_id.journal_id.id })
                

    
    # def action_seller(self):
    #     if self.filtered(lambda so: so.state != 'approve_by_admin'):
    #         raise UserError(_('Only sale orders can be marked as sent directly.'))
    #     for order in self:
    #         order.message_subscribe(partner_ids=order.partner_id.ids)
    #
    #     if self.write({'state': 'approve_by_seller'}):
    #         picking_obj = self.env['stock.picking'].search([('origin','=',self.name)])
    #         picking_obj.write({'payment_provider': self.get_portal_last_transaction().acquirer_id.provider,
    #                            'is_seller_approved': True,
    #                            'hold_state': False })
            
# class SaleOrderLine(models.Model):
#     _inherit = 'sale.order.line'
#
#     @api.depends('qty_invoiced', 'qty_delivered', 'product_uom_qty', 'order_id.state')
#     def _get_to_invoice_qty(self):
#         """
#         Compute the quantity to invoice. If the invoice policy is order, the quantity to invoice is
#         calculated from the ordered quantity. Otherwise, the quantity delivered is used.
#         """
#         for line in self:
#             if line.order_id.state in ['sale', 'done', 'approve_by_admin']:
#                 if line.product_id.invoice_policy == 'order':
#                     line.qty_to_invoice = line.product_uom_qty - line.qty_invoiced
#                 else:
#                     line.qty_to_invoice = line.qty_delivered - line.qty_invoiced
#             else:
#                 line.qty_to_invoice = 0

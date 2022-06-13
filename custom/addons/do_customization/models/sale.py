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

import requests
from odoo import models, fields, api, _
from odoo.addons.website_sale_stock.models.sale_order import SaleOrder as WebsiteSaleStock
import logging
_logger = logging.getLogger(__name__)

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    payment_provider = fields.Selection(selection=[('manual', 'Custom Payment Form'),('transfer', 'Prepaid'),
                                                    ('cash_on_delivery', 'COD')], string='Payment Type')
    payment_upload = fields.Binary(string='Upload Payment')
    payment_upload_name = fields.Char(string='Upload Payment')
    state = fields.Selection([
            ('draft', 'Quotation'),
            ('sent', 'Quotation Sent'),
            ('sale', 'Sales Order'),
            ('approve_by_admin', 'Approved by Admin'),
            ('ready_to_pick', 'Ready to Pick'),
            ('done', 'Locked'),
            ('cancel', 'Cancelled'),
            ], string='Status', readonly=True, copy=False, index=True, tracking=3, default='draft')

    products = fields.Char(string="Products", compute='get_products_string')
    selected_checkout = fields.Boolean(string='Selected For Checkout', defalut=False)

    @api.depends('order_line')
    def get_products_string(self):
        for rec in self:
            products = ''
            for line in rec.order_line:
                if not line.is_delivery:
                    products += line.product_id.name + ' (' + str(int(line.product_qty)) + '), '
            rec.update({
                'products': products or '',
            })

    def action_confirm(self):
        self.ensure_one()
        order = self.env['sale.order.line'].search([('order_id', '=', self.id)])
        order_copy = self.copy()

        for o in order_copy.website_order_line:
            if o.selected_checkout or o.is_delivery:
                o.unlink()

        for o in order:
            if not o.is_delivery:
                if not o.selected_checkout:
                    o.unlink()

        res = super(SaleOrder, self).action_confirm()
        self.write({'payment_provider': self.get_portal_last_transaction().acquirer_id.provider})
        if self.get_portal_last_transaction().acquirer_id.provider == 'cash_on_delivery' and self.state == 'sale':
            self.action_admin()

        if order_copy and self.state in ('sale','approve_by_admin'):
            self.env['website'].newlp_so_website(order_copy)


        order_copy.amount_delivery = 0

        return res
    
    def action_admin(self):
        if self.filtered(lambda so: so.state != 'sale'):
            raise UserError(_('Only sale orders can be marked as sent directly.'))
        for order in self:
            order.message_subscribe(partner_ids=order.partner_id.ids)
        if self.write({'state': 'approve_by_admin'}):
            
            for sol_data in self.env['sale.order.line'].search([('order_id','=',self.id)]):
                sol_data.write({'sol_state': 'approve_by_admin'})
                
            picking_objs = self.env['stock.picking'].search([('origin','=',self.name)])
            delivery_vendor_obj = self.env['res.partner'].search([('delivery_vendor','=', True),('is_default','=', True)], limit=1)
            picking_vendor_obj = self.env['res.partner'].search([('picking_vendor','=', True),('is_default','=', True)], limit=1)
            
            delivery_vendor_obj.delivery_method_ids
            picking_vendor_obj.picking_method_ids
            
            for picking_data in picking_objs:
            
                seller_township = picking_data.marketplace_seller_id.township_id
                if not seller_township:
                    raise Warning("Township cannot be empty for seller %s" % picking_data.marketplace_seller_id.name)
                buyer_township = picking_data.partner_id.township_id
                if not buyer_township:
                    raise Warning("Township cannot be empty for buyer %s" % picking_data.partner_id.name)
                
                pick_all_zone = self.env['picking.method'].search([])
                pickup_zone = None
                delivery_zone = None
                pickup_person = None
                delivery_person = None
                
                for zone in picking_vendor_obj.picking_method_ids:
                    if seller_township in zone.township_ids:
                        pickup_zone = zone
                        
                        for pickup_person_data in picking_vendor_obj.child_ids:
                            if pickup_zone in pickup_person_data.picking_method_ids:
                                pickup_person = pickup_person_data.id
                        
                for d_zone in delivery_vendor_obj.delivery_method_ids:
                    if buyer_township in d_zone.township_ids:
                        delivery_zone = d_zone
                        
                        for delivery_person_data in delivery_vendor_obj.child_ids:
                            if delivery_zone in delivery_person_data.delivery_method_ids:
                                delivery_person = delivery_person_data.id
                                
                if not delivery_zone:
                    raise Warning("Need to setup delivery zone for buyer township %s" % buyer_township.name)
                if not pickup_zone:
                    raise Warning("Need to setup pickup zone for seller township %s" % seller_township.name)
                
                if picking_data.picking_type_id.name == 'Pick':
                    picking_data.write({'payment_provider': self.get_portal_last_transaction().acquirer_id.provider,
                                       'is_admin_approved': True,
                                       'vendor_id': picking_vendor_obj.id or None,
                                       'picking_method_id': pickup_zone.id or None,
                                       'pickup_person_id': pickup_person or None,
                                       'hold_state': False})
        
                    #if self.get_portal_last_transaction().acquirer_id.provider != 'cash_on_delivery':
                    #    picking_data.write({'payment_upload': self.payment_upload, 
                    #                       'paid_amount': self.get_portal_last_transaction().amount, 
                    #                       'payment_remark': self.get_portal_last_transaction().reference,                                   
                    #                       'journal_id': self.get_portal_last_transaction().acquirer_id.journal_id.id })
                        
                elif picking_data.picking_type_id.name == 'Pack':
                    picking_data.write({'payment_provider': self.get_portal_last_transaction().acquirer_id.provider,
                                       'is_admin_approved': True,
                                       'hold_state': False})
        
                    #if self.get_portal_last_transaction().acquirer_id.provider != 'cash_on_delivery':
                    #    picking_data.write({'payment_upload': self.payment_upload, 
                    #                       'paid_amount': self.get_portal_last_transaction().amount, 
                    #                       'payment_remark': self.get_portal_last_transaction().reference,                                   
                    #                       'journal_id': self.get_portal_last_transaction().acquirer_id.journal_id.id })
                
                elif picking_data.picking_type_id.name == 'Delivery Orders':
                        picking_data.write({'payment_provider': self.get_portal_last_transaction().acquirer_id.provider,
                                           'is_admin_approved': True,
                                           'vendor_id': delivery_vendor_obj.id or None,
                                           'delivery_method_id': delivery_zone.id or None,  
                                           'delivery_person_id': delivery_person or None,                                         
                                           'hold_state': False})
            
                        if self.get_portal_last_transaction().acquirer_id.provider != 'cash_on_delivery':
                            picking_data.write({'payment_upload': self.payment_upload, 
                                               'paid_amount': self.get_portal_last_transaction().amount, 
                                               'payment_remark': self.get_portal_last_transaction().reference,                                   
                                               'journal_id': self.get_portal_last_transaction().acquirer_id.journal_id.id })
                            
                        elif self.get_portal_last_transaction().acquirer_id.provider == 'cash_on_delivery':
                            picking_data.write({
                                               'paid_amount': self.get_portal_last_transaction().amount, 
                                               'payment_remark': self.get_portal_last_transaction().reference,                                   
                                               'journal_id': self.get_portal_last_transaction().acquirer_id.journal_id.id })
    
    def action_ready_to_pick(self):
        if self.filtered(lambda so: so.state != 'approve_by_admin'):
            raise UserError(_('Only sale orders can be marked as sent directly.'))
        for order in self:
            order.message_subscribe(partner_ids=order.partner_id.ids)
    
        if self.write({'state': 'ready_to_pick'}):
            
            for sol_data in self.env['sale.order.line'].search([('order_id','=',self.id)]):
                sol_data.write({'sol_state': 'ready_to_pick'})
                
            picking_obj = self.env['stock.picking'].search([('origin','=',self.name)])
            picking_obj.write({'payment_provider': self.get_portal_last_transaction().acquirer_id.provider,
                               'ready_to_pick': True,
                               'hold_state': False })
            
class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    parent_payment_provider = fields.Selection(related='order_id.payment_provider', store=True, readonly=True)
    
    state = fields.Selection([
            ('draft', 'Quotation'),
            ('sent', 'Quotation Sent'),
            ('sale', 'Sales Order'),
            ('approve_by_admin', 'Approved by Admin'),
            ('ready_to_pick', 'Ready to Pick'),
            ('done', 'Done'),
            ('cancel', 'Cancelled'),
        ], related='order_id.state', string='Order Status', readonly=True, copy=False, store=True, default='draft')
    
    sol_state = fields.Selection([            
            ('approve_by_admin', 'Approved by Admin'),
            ('ready_to_pick', 'Ready to Pick'),
            ('done', 'Locked'),
            ('cancel', 'Cancelled'),
            ], string='Order Status', readonly=True, copy=False, store=True, default='approve_by_admin')

    @api.depends('qty_invoiced', 'qty_delivered', 'product_uom_qty', 'order_id.state')
    def _get_to_invoice_qty(self):
        """
        Compute the quantity to invoice. If the invoice policy is order, the quantity to invoice is
        calculated from the ordered quantity. Otherwise, the quantity delivered is used.
        """
        for line in self:
            if line.order_id.state in ['sale', 'done', 'approve_by_admin']:
                if line.product_id.invoice_policy == 'order':
                    line.qty_to_invoice = line.product_uom_qty - line.qty_invoiced
                else:
                    line.qty_to_invoice = line.qty_delivered - line.qty_invoiced
            else:
                line.qty_to_invoice = 0

    def action_ready_to_pick(self):
        
        is_ready_to_pick = True
        
        if self.filtered(lambda sol: sol.state != 'approve_by_admin'):
            raise UserError(_('Only sale order lines can be marked as sent directly.'))
        for order in self:
            order.order_id.message_subscribe(partner_ids=order.order_id.partner_id.ids)
        
        if self.write({'state': 'ready_to_pick', 'sol_state': 'ready_to_pick'}):
            
            for sol_data in self.env['sale.order.line'].search([('order_id','=',self.order_id.id)]):
                if sol_data.state not in ['ready_to_pick', 'cancel'] and not sol_data.is_delivery:
                    is_ready_to_pick = False
                
            if is_ready_to_pick:
                self.order_id.write({'state': 'ready_to_pick'})
                
            picking_obj = self.env['stock.picking'].search([('origin','=',self.order_id.name), ('marketplace_seller_id','=',self.marketplace_seller_id.id)])
            picking_obj.write({'payment_provider': self.order_id.get_portal_last_transaction().acquirer_id.provider,
                               'ready_to_pick': True,
                               'hold_state': False })

    def button_cancel(self):
        
        is_to_update = True #is_to_update parent sale order to ready_to_pick
        
        for rec in self:
            #pickings = rec.mapped('order_id.picking_ids').filtered(lambda picking: picking.marketplace_seller_id.id == rec.marketplace_seller_id.id)
            #pickings.action_cancel()            
            rec.write({'sol_state': 'cancel','state': 'cancel', 'marketplace_state': 'cancel'})
            
            for sol_data in self.env['sale.order.line'].search([('order_id','=',rec.order_id.id)]):
                if sol_data.state not in ['ready_to_pick', 'cancel'] and not sol_data.is_delivery:
                    is_to_update = False
                    
            if is_to_update:
                self.order_id.write({'state': 'ready_to_pick'})
                if rec.marketplace_state == "cancel" and rec.sol_state == 'cancel':
                    rec.write({'state': 'cancel'})
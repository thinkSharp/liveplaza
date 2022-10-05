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
from odoo.exceptions import UserError, ValidationError
from odoo.addons.website_sale_stock.models.sale_order import SaleOrder as WebsiteSaleStock
import logging
import pytz
import datetime
_logger = logging.getLogger(__name__)

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    payment_provider = fields.Selection(selection=[('manual', 'Custom Payment Form'),('transfer', 'Prepaid'),
                                                    ('cash_on_delivery', 'COD'),('wavepay', 'WavePay')], string='Payment Type')
    payment_upload = fields.Binary(string='Upload Payment')
    payment_upload_temp = fields.Binary(string='Upload Payment Temporary')
    payment_upload_name = fields.Char(string='Upload Payment Name')
    selected_payment = fields.Integer(string="Selected Payment", readonly=True)
    selected_carrier_id = fields.Integer(string="Selected Carrier", readonly=True)

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

    delivery_status = fields.Selection([
        ('ordered', 'Ordered'),
        ('picked', 'Picked'),
        ('packed', 'Packed'),
        ('delivering', 'Delivering'),
        ('delivered', 'Delivered')
    ], string='Delivery Status', readonly=True, copy=False, index=True, tracking=3,
        default='ordered',)

    service_delivery_status = fields.Selection([
        ('ordered', 'Ordered'),
        ('delivered', 'Approved / Delivered')
    ], string='Delivery Status', readonly=True, copy=False, index=True, tracking=3, default='ordered')

    picking_date = fields.Datetime('Picking Date', store=True, default="", readonly=True)
    packing_date = fields.Datetime('Packing Date', store=True, default="", readonly=True)
    delivering_date = fields.Datetime('Deliver Date', store=True, default="", readonly=True)
    delivered_date = fields.Datetime('Delivered Date', store=True, default="", readonly=True)

    shipping_method = fields.Selection([
        ('standard', 'Standard'),
        ('express', 'Express')
    ], default='standard')

    @api.model
    def _compute_sol_page_break(self, sol_per_page):
        # to show limited number of sol in a page in printing invoice ( sale report template )
        sol_total_list = []
        sol_list = []
        spp = sol_per_page
        for rec in self.order_line:
            if spp == 0:
                sol_total_list.append(sol_list)
                spp = sol_per_page
                sol_list = []
            if not rec.is_delivery:
                sol_list.append(rec)
                spp = spp - 1
        if len(sol_list) > 0:
            sol_total_list.append(sol_list)
        return sol_total_list

    @api.model
    def _check_delivery_selected(self):
        delivery = 0
        is_all_service = 1
        for line in self.order_line:
            if line.selected_checkout:
                if not (line.product_id.is_service or line.product_id.is_booking_type):
                    is_all_service = 0

        for line in self.order_line:
            if line.is_delivery:
                delivery = 1

        if delivery == 0 and is_all_service == 0:
            return "0"
        return "1"

    @api.depends('state')
    def _compute_type_name(self):
        for record in self:
            if record.state in ('draft', 'sent'):
                record.type_name = _("Quotation")
            elif record.state in ('cancel'):
                record.type_name = _("Cancel")
            else:
                record.type_name = _('Sales Order')

    def _website_product_id_change(self, order_id, product_id, qty=0):
        res = super(SaleOrder, self)._website_product_id_change(
            order_id, product_id, qty)

        order = self.sudo().browse(order_id)
        product_context = dict(self.env.context)
        product_context.setdefault('lang', order.partner_id.lang)
        product_context.update({
            'partner': order.partner_id,
            'quantity': qty,
            'date': order.date_order,
            'pricelist': order.pricelist_id.id,
            'force_company': order.company_id.id,
        })
        product = self.env['product.product'].with_context(product_context).browse(product_id)
        discount = 0
        discount_amount = 0

        if order.pricelist_id.discount_policy == 'without_discount' and not product.is_booking_type:
            # This part is pretty much a copy-paste of the method '_onchange_discount' of
            # 'sale.order.line'.
            price, rule_id = order.pricelist_id.with_context(product_context).get_product_price_rule(product,
                                                                                                     qty or 1.0,
                                                                                                     order.partner_id)
            pu, currency = self.env['sale.order.line'].with_context(product_context)._get_real_price_currency(
                product, rule_id, qty, product.uom_id, order.pricelist_id.id)
            if pu != 0:
                if order.pricelist_id.currency_id != currency:
                    # we need new_list_price in the same currency as price, which is in the SO's pricelist's currency
                    date = order.date_order or fields.Date.today()
                    pu = currency._convert(pu, order.pricelist_id.currency_id, order.company_id, date)

                item_ids = order.pricelist_id.item_ids
                compute_price = ""
                for item in item_ids:
                    if product.name == item.product_tmpl_id.name:
                        compute_price = item.compute_price
                        break

                if compute_price == 'percentage':
                    discount = (pu - price) / pu * 100
                    if discount < 0:
                        # In case the discount is negative, we don't want to show it to the customer,
                        # but we still want to use the price defined on the pricelist
                        discount = 0
                        pu = price
                elif compute_price == 'fixed_discount':
                    discount_amount = pu - price
                else:
                    pu = product.price
                    if order.pricelist_id and order.partner_id:
                        order_line = order._cart_find_product_line(product.id)
                        if order_line:
                            pu = self.env['account.tax']._fix_tax_included_price_company(pu, product.taxes_id,
                                                                                         order_line[0].tax_id,
                                                                                         self.company_id)

        else:
            pu = product.price
            if order.pricelist_id and order.partner_id:
                order_line = order._cart_find_product_line(product.id)
                if order_line:
                    pu = self.env['account.tax']._fix_tax_included_price_company(pu, product.taxes_id,
                                                                                 order_line[0].tax_id, self.company_id)

        return {
            'product_id': product_id,
            'product_uom_qty': qty,
            'order_id': order_id,
            'product_uom': product.uom_id.id,
            'price_unit': pu,
            'discount': discount,
            'discount_amount': discount_amount,
        }

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
        order_lines = self.env['sale.order.line'].search([('order_id', '=', self.id)])
        copy_or_not = False
        order_copy = self.env['sale.order']
        
        for iscopy in self.website_order_line:
            if not iscopy.selected_checkout:
                copy_or_not = True
            
        if copy_or_not:
            order_copy = self.copy()       
        
        if order_copy:
            for mma in order_copy.order_line:
                if mma.selected_checkout or mma.is_delivery:
                    mma.unlink()
                    
            for o in order_copy.website_order_line:
                if o.selected_checkout or o.is_delivery:
                    o.unlink()

        for o in order_lines:
            if not o.is_delivery:
                if not o.selected_checkout:
                    o.unlink()

        res = super(SaleOrder, self).action_confirm()
        self.write({'payment_provider': self.get_portal_last_transaction().acquirer_id.provider})
        for line_status in self.order_line:
            line_status.write({'sol_state': self.state})
        #if self.get_portal_last_transaction().acquirer_id.provider in ('wavepay','cash_on_delivery') and self.state == 'sale':
        #    self.action_admin()

        if order_copy and self.state in ('sale','approve_by_admin'):
            self.env['website'].newlp_so_website(order_copy)

        if order_copy:
            order_copy.amount_delivery = 0
            order_copy.selected_carrier_id = ''

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
            
            for sol_data in self.env['sale.order.line'].search([('order_id','=',self.id),('sol_state','!=','cancel')]):
                sol_data.write({'sol_state': 'ready_to_pick'})
                
            picking_obj = self.env['stock.picking'].search([('origin','=',self.name)])
            picking_obj.write({'payment_provider': self.get_portal_last_transaction().acquirer_id.provider,
                               'ready_to_pick': True,
                               'hold_state': False })

    def action_cancel(self):
        if self.write({'state': 'cancel'}):    
            for sol_data in self.env['sale.order.line'].search([('order_id','=',self.id)]):
                sol_data.write({'sol_state': 'cancel'})
                
            
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
            ('draft', 'Quotation'),
            ('sent', 'Quotation Sent'),
            ('sale', 'Sales Order'),         
            ('approve_by_admin', 'Approved by Admin'),
            ('ready_to_pick', 'Ready to Pick'),
            ('done', 'Locked'),
            ('cancel', 'Cancelled'),
            ], string='Order Status', readonly=True, copy=False, store=True, default='draft')

    delivery_status = fields.Selection([
        ('ordered', 'Ordered'),
        ('picked', 'Picked'),
        ('packed', 'Packed'),
        ('delivering', 'Delivering'),
        ('delivered', 'Delivered'),
        ('hold', 'Hold'),
        ('cancel', 'Cancelled')
    ], string='Delivery Status', readonly=True, copy=False, index=True, tracking=3, default='ordered')

    old_delivery_status = fields.Char(string="Old Status", readonly=True, store=True)

    service_delivery_status = fields.Selection([
        ('ordered', 'Ordered'),
        ('delivered', 'Approved / Delivered'),
    ], string='Delivery Status', readonly=True, copy=False, index=True, tracking=3, default='ordered')

    picking_date = fields.Datetime('Picking Date', store=True, default="", readonly=True)
    packing_date = fields.Datetime('Packing Date', store=True, default="", readonly=True)
    delivering_date = fields.Datetime('Deliver Date', store=True, default="", readonly=True)
    delivered_date = fields.Datetime('Delivered Date', store=True, default="", readonly=True)
    confirmed_date = fields.Datetime('Confirmed Date', store=True, default="", readonly=True)

    discount_amount = fields.Float(string='Discount Amount', digits='Discount', default=0.0)
    hold_reason = fields.Char('Hold Reason', store=True, readonly=True)

    @api.depends('product_uom_qty', 'discount', 'discount_amount', 'price_unit', 'tax_id')
    def _compute_amount(self):
        super(SaleOrderLine, self)._compute_amount()

        for line in self:

            if line.discount_amount > 0:
                price = line.price_unit - line.discount_amount
            else:
                price = line.price_unit * (1 - (line.discount or 0.0) / 100.0)

            taxes = line.tax_id.compute_all(price, line.order_id.currency_id, line.product_uom_qty,
                                            product=line.product_id, partner=line.order_id.partner_shipping_id)
            line.update({
                'price_tax': sum(t.get('amount', 0.0) for t in taxes.get('taxes', [])),
                'price_total': taxes['total_included'],
                'price_subtotal': taxes['total_excluded'],
            })
            if self.env.context.get('import_file', False) and not self.env.user.user_has_groups(
                    'account.group_account_manager'):
                line.tax_id.invalidate_cache(['invoice_repartition_line_ids'], [line.tax_id.id])

    def change_datetime_format(self, d):
        if d:
            tz = d.astimezone(pytz.timezone('Asia/Yangon'))
            return tz.strftime("%d %b %Y - %H:%M")
        else:
            return ""

    @api.model
    def get_sol_delivery_progress(self):
        # for sale order which only booking products
        create_date = self.change_datetime_format(self.create_date)
        picking_date = self.change_datetime_format(self.picking_date)
        packing_date = self.change_datetime_format(self.packing_date)
        delivering_date = self.change_datetime_format(self.delivering_date)
        delivered_date = self.change_datetime_format(self.delivered_date)
        delivery_state = []
        delivery_completion = []

        # service product
        if self.product_id.is_service or self.product_id.is_booking_type:
            delivery_status = {'delivered': 'complete', 'ordered': 'complete'}
            status = self.service_delivery_status
        else:
            delivery_status = {'delivered': "complete", 'delivering': 'complete', 'packed': 'complete',
                               'picked': 'complete',
                               'ordered': 'complete'}

            status = self.delivery_status


        for s in delivery_status.keys():
            if s == status:
                if s == 'delivering':
                    delivery_status[s] = 'current'
                break
            else:
                delivery_status[s] = 'not_yet'

        for s, p in delivery_status.items():
            delivery_state.append(s)
            delivery_completion.append(p)

        delivery_state.reverse()
        delivery_completion.reverse()

        delivery_progress = {state: {} for state in delivery_state}
        delivery_dates = [create_date, picking_date, packing_date,
                          delivering_date, delivered_date]

        for i in range(len(delivery_state)):
            delivery_progress[delivery_state[i]] = [delivery_completion[i], delivery_dates[i]]

        return delivery_progress

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
                
                for sol_data2 in self.env['sale.order.line'].search([('order_id','=',self.order_id.id), ('is_delivery' , '=' , True)]):
                    sol_data2.write({'sol_state':self.order_id.state})
                if (self.env['sale.order.line'].search([('order_id','=',self.order_id.id), ('sol_state' , '=' , 'cancel')]) and self.product_id.is_service)  or (self.env['sale.order.line'].search([('order_id','=',self.order_id.id), ('sol_state' , '=' , 'cancel')]) and self.product_id.is_booking_type):
                    for cancel_deli_service in self.env['sale.order.line'].search([('order_id','=',self.order_id.id), ('is_delivery' , '=' , True)]):
                        cancel_deli_service.write({'sol_state':'cancel'})
                
            picking_obj = self.env['stock.picking'].search([('origin','=',self.order_id.name), ('order_line_id','=',self.id),
                                                            ('marketplace_seller_id','=',self.marketplace_seller_id.id)])
            if picking_obj:
                picking_obj.write({'payment_provider': self.order_id.get_portal_last_transaction().acquirer_id.provider,
                               'ready_to_pick': True,
                               'hold_state': False })

    def price_cancel(self):
        """
        Compute the total amounts of the SO after Order Cancel.
        """ 
        for line in self:
            for order in self.order_id:
                amount_untaxed = order.amount_untaxed
                amount_tax = order.amount_tax
                if self.env['sale.order.line'].search([('order_id','=',line.order_id.id), ('sol_state' , '=' , 'cancel')]):
                    amount_untaxed -= line.price_subtotal
                    amount_tax += line.price_tax

                order.update({
                    'amount_untaxed': order.pricelist_id.currency_id.round(amount_untaxed),
                    'amount_tax': order.pricelist_id.currency_id.round(amount_tax),
                    'amount_total': amount_untaxed + amount_tax,
                })
                # For Delivery Charge Price Cancel
                for sol_data in self.env['sale.order.line'].search([('order_id','=',line.order_id.id), ('is_delivery' , '=' , True), ('sol_state' , '=' , 'cancel')]):
                    amount_untaxed -= sol_data.price_subtotal
                    amount_tax += sol_data.price_tax
                    sol_data.order_id.update({
                        'amount_untaxed': sol_data.order_id.pricelist_id.currency_id.round(amount_untaxed),
                        'amount_tax': sol_data.order_id.pricelist_id.currency_id.round(amount_tax),
                        'amount_total': amount_untaxed + amount_tax,
                    })


    def button_cancel(self):
        
        is_to_update = True #is_to_update parent sale order to ready_to_pick or cancel
        count = 0 #To count ready_to_pick
        rdy_count = 0
        
        for rec in self:
            #pickings = rec.mapped('order_id.picking_ids').filtered(lambda picking: picking.marketplace_seller_id.id == rec.marketplace_seller_id.id)
            #pickings.action_cancel()            
            rec.write({'sol_state': 'cancel','state': 'cancel', 'marketplace_state': 'cancel'})
            rec.write({'delivery_status': 'cancel'})
            print("Sale order line is cancelled.")

            solines = self.env['sale.order.line'].search([('order_id','=',rec.order_id.id)])
            final_sol = True
            for soline in solines:
                if soline.sol_state != 'cancel' and not soline.is_delivery:
                    final_sol = False

            print("I am")
            if final_sol:
               print("Final SaLE ORDER")
               sms_template_objs = self.env["wk.sms.template"].sudo().search(
                   [('condition', '=', 'final_sale_order_line_cancel'), ('globally_access', '=', False)])
            else:
                sms_template_objs = self.env["wk.sms.template"].sudo().search(
                    [('condition', '=', 'sale_order_line_cancel'), ('globally_access', '=', False)])
            for sms_template_obj in sms_template_objs:
                mobile = sms_template_obj._get_partner_mobile(self.order_id.partner_id)
                if mobile:
                    sms_template_obj.send_sms_using_template(
                        mobile, sms_template_obj, obj=self)

            if rec.sol_state == 'cancel':
                picking_obj = self.env['stock.picking'].search([('origin','=',self.order_id.name), ('order_line_id','=',rec.id),
                                                            ('marketplace_seller_id','=',rec.marketplace_seller_id.id)])
                for i_data in picking_obj:
                    i_data.action_cancel()
                    
            for sol_data in self.env['sale.order.line'].search([('order_id','=',rec.order_id.id)]):
                if sol_data.state not in ['ready_to_pick', 'cancel'] and not sol_data.is_delivery:
                    is_to_update = False
            
            if self.env['sale.order.line'].search([('order_id','=',rec.order_id.id), ('sol_state' , '=' , 'ready_to_pick')]):
                count += 1
         
            for ready in self.env['sale.order.line'].search([('order_id','=',rec.order_id.id)]):
                if ready.state in ['ready_to_pick'] and not (ready.product_id.is_service or ready.product_id.is_booking_type):
                    rdy_count +=1
     
            for sol_data2 in self.env['sale.order.line'].search([('order_id','=',rec.order_id.id)]):
                    
                if sol_data2.state in ['ready_to_pick', 'cancel']:
                    if is_to_update:
                        if count == 0:
                            self.order_id.write({'state': 'cancel'})
                            if rec.marketplace_state == "cancel" and rec.sol_state == 'cancel':
                                rec.write({'state': 'cancel'})

                        elif count >= 1:
                            self.order_id.write({'state': 'ready_to_pick'})

                        for sol_data3 in self.env['sale.order.line'].search([('order_id','=',rec.order_id.id), ('is_delivery' , '=' , True)]):
                            sol_data3.write({'sol_state':rec.order_id.state})
                            
                        if count >= 1:
                            for sol_data4 in self.env['sale.order.line'].search([('order_id','=',rec.order_id.id)]):
                                if sol_data4.product_id.is_service or sol_data4.product_id.is_booking_type:
                                    if rdy_count == 0:
                                        for cancel_deli_service in self.env['sale.order.line'].search([('order_id','=',self.order_id.id), ('is_delivery' , '=' , True)]):
                                            cancel_deli_service.write({'sol_state':'cancel'})
                                    elif rdy_count >= 1:
                                        for sol_data5 in self.env['sale.order.line'].search([('order_id','=',rec.order_id.id), ('is_delivery' , '=' , True)]):
                                            sol_data5.write({'sol_state':rec.order_id.state})
                  
        return self.price_cancel()
            

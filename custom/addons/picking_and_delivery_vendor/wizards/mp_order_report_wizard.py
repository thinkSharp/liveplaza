# -*- coding: utf-8 -*-

from odoo import api, fields, models, tools, _
from datetime import datetime

from odoo.exceptions import ValidationError,UserError, Warning

class MarketplaceOrderResultWizard(models.TransientModel):
    _name = 'mp.order.result.wizard'
    
    start_date = fields.Date('Start Date', default=datetime.today())
    end_date = fields.Date('End Date', default=datetime.today())
    
    def generate_order_report(self):
        vals = []
        
        records = self.env['mp.order.result'].search([])
        
        if records:
            records.unlink()
                    
        domain = [('create_date', '>=', self.start_date), ('create_date', '<=', self.end_date), ('marketplace_seller_id', '!=', False)]
        order_records = self.env['sale.order.line'].search(domain)
        
        for order_record in order_records:
            mp_order = order_record.display_name
            mp_product_name = order_record.product_id.name
            mp_customer_name = order_record.order_partner_id.name
            mp_order_date = order_record.create_date
            mp_order_qty = order_record.product_uom_qty
            mp_subtotal = order_record.price_subtotal
            mp_seller_name = order_record.marketplace_seller_id.name
            
            if order_record.marketplace_state == 'approved' and order_record.is_picked == False and order_record.is_packaged == False:
                mp_order_state = 'approved'
            elif order_record.marketplace_state == 'approved' and order_record.is_picked == True and order_record.is_packaged == False:
                mp_order_state = 'picked'
            elif order_record.marketplace_state == 'approved' and order_record.is_picked == True and order_record.is_packaged == True:
                mp_order_state = 'packaged'
            elif order_record.marketplace_state == 'shipped' :
                mp_order_state = 'shipped'
            elif order_record.marketplace_state == 'cancel':
                mp_order_state = 'cancel'
                
            pickings = order_record.mapped('order_id.picking_ids').filtered(lambda picking: picking.marketplace_seller_id.id == order_record.marketplace_seller_id.id)
            for picking in pickings:
                mp_journal = picking.journal_id.name
                if picking.journal_id.id == 25:
                    if order_record.marketplace_state == 'shipped' and order_record.is_paid == False:
                        mp_payment_state = 'collected'
                    elif order_record.marketplace_state == 'shipped' and order_record.is_paid == True:
                        mp_payment_state = 'paid'
                    else:
                        mp_payment_state = 'open'
                else:
                    if order_record.marketplace_state == 'shipped' and order_record.is_paid == True:
                        mp_payment_state = 'paid'
                    else:
                        mp_payment_state = 'open'
                            
            res = {
                    'mp_order': mp_order,
                    'mp_product_name': mp_product_name,
                    'mp_customer_name': mp_customer_name,
                    'mp_order_date': mp_order_date,
                    'mp_order_qty': mp_order_qty,
                    'mp_subtotal': mp_subtotal,
                    'mp_journal': mp_journal,
                    'mp_seller_name': mp_seller_name,
                    'mp_order_state': mp_order_state,
                    'mp_payment_state': mp_payment_state,
                }
        
            vals.append(res)
            
        if vals:
            self.env['mp.order.result'].create(vals)
            wizard_form = self.env.ref('mp_order_result_tree', False)
                
            return {
                'name': 'Marketplace Orders',
                'type': 'ir.actions.act_window',
                'view_type': 'form',
                'view_mode': 'tree',
                'res_model': 'mp.order.result',
                'views': [(wizard_form, 'tree')],
                # 'domain' : [('mp_seller_name','=', self.env.user.partner_id.name)],
                'target': 'current',
            }
        else:
            raise ValidationError(_("No records found."))


class MarketplaceOrderResult(models.TransientModel):
    _name = 'mp.order.result'
    
    mp_order = fields.Char('Order Ref')
    mp_product_name = fields.Char('Product')
    mp_customer_name = fields.Char('Customer')
    mp_order_date = fields.Date('Date')
    mp_order_qty = fields.Float('Ordered Qty')
    mp_subtotal = fields.Float('Subtotal')
    mp_seller_name = fields.Char('Seller')
    mp_journal = fields.Char('Type')
    mp_order_state = fields.Selection([
        ('approved', 'Approved'),
        ('picked', 'Picked'),
        ('packaged', 'Packaged'),
        ('shipped', 'Shipped'),
        ('cancel', 'Cancelled')],
        'State')
    mp_payment_state = fields.Selection([
        ('open', 'Open'),
        ('collected', 'Collected'),
        ('paid', 'Paid')],
        'State')
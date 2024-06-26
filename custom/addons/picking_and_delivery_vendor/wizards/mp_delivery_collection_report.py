# -*- coding: utf-8 -*-

from odoo import api, fields, models, tools, _
from datetime import datetime

from odoo.exceptions import ValidationError,UserError, Warning

class MarketplaceDeliveryCollectionResultWizard(models.TransientModel):
    _name = 'mp.delivery.collection.result.wizard'
    
    start_date = fields.Date('Start Date', default=datetime.today())
    end_date = fields.Date('End Date', default=datetime.today())
    payment_type_param = fields.Selection([('cash_on_delivery', 'COD'),
                                    ('transfer', 'Prepaid'), ('both', 'Both')], string="Payment Type", default="both")
    marketplace_seller_id = fields.Many2one('res.partner', string='Seller', domain=[('seller', '=', True)], copy=False)
    delivery_vendor_id = fields.Many2one('res.partner', string='Delivery Vendor', domain="[('company_type', '=', 'company'), ('delivery_vendor', '=', True)]", copy=False)
    
    def generate_order_report(self):
        vals = []
        
        records = self.env['mp.delivery.collection.result'].search([])
        
        if records:
            records.unlink()
                             
           
        do_pick_type = self.env['stock.picking.type'].search([('name', '=', 'Delivery Orders')])
        
        domain = [('create_date', '>=', self.start_date), ('create_date', '<=', self.end_date), ('picking_type_id', '=', do_pick_type.id), 
                  ('marketplace_seller_id', '!=', False)]
        
        if self.payment_type_param != "both":
            domain.append(('payment_provider', '=', self.payment_type_param))
        if self.marketplace_seller_id:
            domain.append(('marketplace_seller_id', '=', self.marketplace_seller_id.id))
        if self.delivery_vendor_id:
            domain.append(('vendor_id', '=', self.delivery_vendor_id.id))

        order_records = self.env['stock.picking'].search(domain, order='id desc')
        
        for order_record in order_records:
            mp_name = order_record.sale_id.display_name
            mp_customer_name = order_record.partner_id.name
            mp_paid_date = order_record.date_done
            mp_receivable_amount = order_record.receivable_amount_stored
            mp_delivery_amount = order_record.delivery_amount_stored
            mp_paid_amount = order_record.paid_amount
            mp_vendor_name = order_record.vendor_id.name
            mp_payment_type = order_record.journal_id.name
            if order_record.payment_provider == "transfer":
                mp_payment_provider = "Prepaid"
            elif order_record.payment_provider == "cash_on_delivery":
                mp_payment_provider = "COD"
            
            
            sale_domain = [('id', '=', order_record.sale_id.id)]
            sale_record = self.env['sale.order'].search(sale_domain)            
            
            if sale_record:
                mp_order_date = sale_record.date_order
                mp_amount_total = sale_record.amount_total
                            
            merge_domain = [('sale_id.name', '=', mp_name)]
            merge_records = self.env['stock.picking'].search(merge_domain)
            paid_total = 0.0
            
            for merge_record in merge_records:
                paid_total += merge_record.paid_amount
                            
            if paid_total <= 0:
                mp_paid_state = 'new'
            elif paid_total >= mp_amount_total:
                mp_paid_state = 'paid'
            else:
                mp_paid_state = 'partial'
            
            res = {
                    'mp_name': mp_name,
                    'mp_customer_name': mp_customer_name,
                    'mp_order_date': mp_order_date,
                    'mp_paid_date': mp_paid_date,
                    'mp_amount_total': mp_amount_total,
                    'mp_receivable_amount': mp_receivable_amount,
                    'mp_delivery_amount': mp_delivery_amount,
                    'mp_paid_amount': mp_paid_amount,
                    'mp_vendor_name': mp_vendor_name,
                    'mp_payment_type': mp_payment_type,
                    'mp_payment_provider': mp_payment_provider,
                    'mp_paid_state': mp_paid_state,
                }
        
            vals.append(res)
            
        if vals:
            self.env['mp.delivery.collection.result'].create(vals)
            wizard_form = self.env.ref('mp_delivery_collection_result_tree', False)
                
            return {
                'name': 'Delivery Collection',
                'type': 'ir.actions.act_window',
                'view_type': 'form',
                'view_mode': 'tree',
                'res_model': 'mp.delivery.collection.result',
                'views': [(wizard_form, 'tree')],
                'target': 'current',
            }
        else:
            raise ValidationError(_("No records found."))


class MarketplaceDeliveryCollectionResult(models.TransientModel):
    _name = 'mp.delivery.collection.result'
    
    mp_name = fields.Char('Order Reference')
    mp_order_date = fields.Date('Order Date')
    mp_paid_date = fields.Date('Paid Date')
    mp_customer_name = fields.Char('Customer')
    mp_amount_total = fields.Float('Total Amount')
    mp_delivery_amount = fields.Float('Delivery Amount')
    mp_receivable_amount = fields.Float('Receivable Amount')
    mp_paid_amount = fields.Float('Paid Amount')
    mp_vendor_name = fields.Char('Delivery Vendor')
    mp_payment_type = fields.Char('Payment Type')
    mp_payment_provider = fields.Char('Payment Provider')
    mp_paid_state = fields.Selection([
        ('new', 'New'),
        ('partial', 'Partially Paid'),
        ('paid', 'Paid')],
        'Payment State')
    
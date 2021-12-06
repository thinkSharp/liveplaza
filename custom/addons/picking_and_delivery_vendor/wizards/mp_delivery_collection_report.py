# -*- coding: utf-8 -*-

from odoo import api, fields, models, tools, _
from datetime import datetime

from odoo.exceptions import ValidationError,UserError, Warning

class MarketplaceDeliveryCollectionResultWizard(models.TransientModel):
    _name = 'mp.delivery.collection.result.wizard'
    
    start_date = fields.Date('Start Date', default=datetime.today())
    end_date = fields.Date('End Date', default=datetime.today())
    
    def generate_order_report(self):
        vals = []
        
        records = self.env['mp.delivery.collection.result'].search([])
        
        if records:
            records.unlink()
                                
        domain = [('create_date', '>=', self.start_date), ('create_date', '<=', self.end_date), ('marketplace_seller_id', '!=', False)]
        order_records = self.env['stock.picking'].search(domain)
        
        
        
        for order_record in order_records:
            mp_name = order_record.sale_id.display_name
            mp_customer_name = order_record.partner_id.name
            mp_paid_date = order_record.date_done
            mp_paid_amount = order_record.paid_amount
            mp_vendor_name = order_record.vendor_id.name
            mp_payment_type = order_record.journal_id.name
            
            
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
                    'mp_paid_amount': mp_paid_amount,
                    'mp_vendor_name': mp_vendor_name,
                    'mp_payment_type': mp_payment_type,
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
    mp_paid_amount = fields.Float('Paid Amount')
    mp_vendor_name = fields.Char('Delivery Vendor')
    mp_payment_type = fields.Char('Payment Type')
    mp_paid_state = fields.Selection([
        ('new', 'New'),
        ('partial', 'Partially Paid'),
        ('paid', 'Paid')],
        'Payment State')
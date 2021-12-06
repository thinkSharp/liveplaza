# -*- coding: utf-8 -*-

from odoo import api, fields, models, tools, _
from datetime import datetime


from odoo.exceptions import ValidationError,UserError, Warning

class MarketplaceDeliveryVendorReceivableResultWizard(models.TransientModel):
    _name = 'mp.delivery.vendor.receivable.result.wizard'
    
    def generate_order_report(self):
        vals = []
        
        records = self.env['mp.delivery.vendor.receivable.result'].search([])
        
        if records:
            records.unlink()
                                
        domain = [('delivery_vendor', '=', True)]
        vendor_records = self.env['res.partner'].search(domain)
        
        for vendor_record in vendor_records:
            mp_delivery_name = vendor_record.name
            mp_active_vendor = vendor_record.active_delivery 
            mp_to_pay_amount = -(vendor_record.debit)          
                       
            pickings = self.env['stock.picking'].search([('journal_id', '=', 25), ('vendor_id', '=', vendor_record.id), ('state', '=', 'done')])

            mp_collected_amount = 0.0
            
            if pickings:
                for picking in pickings:
                    mp_collected_amount += picking.paid_amount
                    
            
            res = {
                    'mp_delivery_name': mp_delivery_name,
                    'mp_active_vendor': mp_active_vendor,
                    'mp_collected_amount': mp_collected_amount,
                    'mp_to_pay_amount': mp_to_pay_amount,
                }
        
            vals.append(res)
            
        if vals:
            self.env['mp.delivery.vendor.receivable.result'].create(vals)
            wizard_form = self.env.ref('mp_delivery_vendor_receivable_result_tree', False)
                
            return {
                'name': 'Delivery Vendor Receivable',
                'type': 'ir.actions.act_window',
                'view_type': 'form',
                'view_mode': 'tree',
                'res_model': 'mp.delivery.vendor.receivable.result',
                'views': [(wizard_form, 'tree')],
                'target': 'current',
            }
        else:
            raise ValidationError(_("No records found."))


class MarketplaceDeliveryVendorReceivableResult(models.TransientModel):
    _name = 'mp.delivery.vendor.receivable.result'
    
    mp_delivery_name = fields.Char('Delivery Person')
    mp_active_vendor = fields.Boolean('Active')
    mp_collected_amount = fields.Float('Collected Amount')
    mp_to_pay_amount = fields.Float('Receivable Amount')
    
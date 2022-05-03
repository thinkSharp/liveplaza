# -*- coding: utf-8 -*-

from odoo import api, fields, models, tools, _
from datetime import datetime

from odoo.exceptions import ValidationError,UserError, Warning

class MarketplaceDeliveryWizard(models.TransientModel):
    _name = 'mp.delivery.wizard'
    
    start_date = fields.Date('Start Date', default=datetime.today())
    end_date = fields.Date('End Date', default=datetime.today())    
    vendor_id = fields.Many2one('res.partner', string='Delivery Vendor', required = True , domain=[('delivery_vendor', '=', True)], copy=False)

    def generate_order_report(self):
        vals = []
        vendor_data = {}
        
        records = self.env['mp.delivery.result'].search([])
        
        if records:
            records.unlink()
        
        if self.vendor_id:
            vendor_data = self._calculate_delivery_payment(self.vendor_id, self.start_date, self.end_date)            
                            
        res = {
                'start_date': self.start_date,
                'end_date': self.end_date,
                'report_date': datetime.today(),
                
                'mp_vendor_name': self.vendor_id.name,

                'total_mp_payable_by_vendor': vendor_data.get("total_mp_payable_by_vendor"),
                'delivery_payable_by_company': vendor_data.get("delivery_payable_by_company"),
                'deli_com_paid': vendor_data.get("deli_com_paid"),
                'mp_vendor_paid': vendor_data.get("mp_vendor_paid"),
                'deli_com_balance': vendor_data.get("deli_com_balance"),
                'mp_vendor_balance': vendor_data.get("mp_vendor_balance"),
            }
    
        vals.append(res)
            
        if vals:
            self.env['mp.delivery.result'].create(vals)
            wizard_form = self.env.ref('mp_delivery_result_tree', False)
                
            return {
                'name': 'Marketplace Delivery',
                'type': 'ir.actions.act_window',
                'view_type': 'form',
                'view_mode': 'tree',
                'res_model': 'mp.delivery.result',
                'views': [(wizard_form, 'tree')],
                # 'domain' : [('mp_seller_name','=', self.env.user.partner_id.name)],
                'target': 'current',
            }
        else:
            raise ValidationError(_("No records found."))

    def _calculate_delivery_payment(self,vendor_id, start_date, end_date):
        for obj in vendor_id:
            if obj.delivery_vendor:
                so_list = []
                delivery_payable_by_company = total_mp_payable_by_vendor = mp_vendor_paid = deli_com_paid = 0

                picking_type_id = self.env["stock.picking.type"].search([("name", "=", 'Delivery Orders')])
                spicking_obj = self.env["stock.picking"].search([ ("vendor_id", "=", obj.id), ("state", "=", "done"),
                                                    ("picking_type_id", "=", self.env["stock.picking.type"].search([("name", "=", 'Delivery Orders')]).id )])
                for do_line in spicking_obj:
                    if do_line.origin not in so_list:
                        so_id = self.env["sale.order"].search([("name", "=", do_line.origin)])
                        if so_id and so_id.payment_provider == "transfer":
                            sol_objs = self.env["sale.order.line"].search([("order_id", "=", so_id.id )])
                            for sol_line in sol_objs:
                                if sol_line.is_delivery:
                                    delivery_payable_by_company += abs(sol_line.price_subtotal)
                                    so_list.append(do_line.origin)
                        elif so_id and so_id.payment_provider == "cash_on_delivery":
                            sol_objs = self.env["sale.order.line"].search([("order_id", "=", so_id.id )])
                            for sol_line in sol_objs:
                                if not sol_line.is_delivery:
                                    total_mp_payable_by_vendor += abs(sol_line.price_subtotal)
                                    so_list.append(do_line.origin)
                         
                do_payment_objs = self.env["delivery.payment"].search([("vendor_id", "=", obj.id), ("payment_state", "not in",["draft", "confirm"])])
                for do_payment in do_payment_objs:
                    #Calculate total marketplace payment for seller
                    if do_payment.payment_state == 'done' and do_payment.payment_mode == "order_paid":
                        mp_vendor_paid += abs(do_payment.total_amount)

                    #Calculate total paid marketplace payment for seller
                    if do_payment.payment_state == 'done' and do_payment.payment_mode == "delivery_payment":
                        deli_com_paid += abs(do_payment.total_amount)
                                     
                return {
                    'total_mp_payable_by_vendor': total_mp_payable_by_vendor,
                    'delivery_payable_by_company': delivery_payable_by_company,
                    'deli_com_paid': deli_com_paid,
                    'mp_vendor_paid': mp_vendor_paid,
                    'deli_com_balance': abs(delivery_payable_by_company - deli_com_paid),
                    'mp_vendor_balance': abs(total_mp_payable_by_vendor - mp_vendor_paid),
                    }


class MarketplaceDeliveryResult(models.TransientModel):
    _name = 'mp.delivery.result'
    
    start_date = fields.Date('From Date')
    end_date = fields.Date('To Date')  
    report_date = fields.Date('Report Date', default=datetime.today())
      
    mp_vendor_name = fields.Char('Delivery Vendor')
    
    total_mp_payable_by_vendor = fields.Float('Total Payable to Delivery Vendor')
    delivery_payable_by_company = fields.Float('Total Receivable from Delivery Vendor')
    deli_com_paid = fields.Float(string="Delivery Fees Paid via Prepaid")
    mp_vendor_paid = fields.Float(string="Order Paid via COD")
    deli_com_balance = fields.Float(string="Delivery Fees Balance via Prepaid")
    mp_vendor_balance = fields.Float(string="Order Balance via COD")



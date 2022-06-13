# -*- coding: utf-8 -*-

from odoo import api, fields, models, tools, _
from datetime import datetime

from odoo.exceptions import ValidationError,UserError, Warning

class MarketplaceCommissiontWizard(models.TransientModel):
    _name = 'mp.commission.wizard'
    
    start_date = fields.Date('Start Date', default=datetime.today())
    end_date = fields.Date('End Date', default=datetime.today())    
    marketplace_seller_id = fields.Many2one('res.partner', string='Seller', required = True , domain=[('seller', '=', True)], copy=False)
    
    def generate_order_report(self):
        vals = []
        seller_data = {}
        
        records = self.env['mp.commission.result'].search([])
        
        if records:
            records.unlink()
        
        domain = [('create_date', '>=', self.start_date), ('create_date', '<=', self.end_date), 
                  ('marketplace_seller_id', '!=', False)]
        
        if self.marketplace_seller_id:
            seller_data = self.calculate_mp_related_payment_commission(self.marketplace_seller_id, self.start_date, self.end_date)            
                            
        res = {
                'start_date': self.start_date,
                'end_date': self.end_date,
                'report_date': datetime.today(),
                
                'mp_seller_name': self.marketplace_seller_id.name,

                'mp_commission_amount': seller_data.get("total_commission_payment"),
                'mp_total_mp_payment': seller_data.get("total_mp_payment"),
                'mp_paid_mp_payment': seller_data.get("paid_mp_payment"),
                'mp_balance_mp_payment': seller_data.get("balance_mp_payment"),
            }
    
        vals.append(res)
            
        if vals:
            self.env['mp.commission.result'].create(vals)
            wizard_form = self.env.ref('mp_commission_result_tree', False)
                
            return {
                'name': 'Marketplace Commissions',
                'type': 'ir.actions.act_window',
                'view_type': 'form',
                'view_mode': 'tree',
                'res_model': 'mp.commission.result',
                'views': [(wizard_form, 'tree')],
                # 'domain' : [('mp_seller_name','=', self.env.user.partner_id.name)],
                'target': 'current',
            }
        else:
            raise ValidationError(_("No records found."))

    def calculate_mp_related_payment_commission(self,seller,start_date,end_date):
       
        if seller:
            total_mp_payment = paid_mp_payment = cashable_amount = total_commission_payment = 0
            
            sol_objs = self.env["sale.order.line"].search([("marketplace_seller_id", "=", seller.id), ("is_delivery", "=", False),
                                                           ('create_date', '>=', start_date), ('create_date', '<=', end_date)])
            picking_type_id = self.env["stock.picking.type"].search([("name", "=", 'Delivery Orders')])
            
            for sol_line in sol_objs:
                spicking_obj = self.env["stock.picking"].search([("origin", "=", sol_line.order_id.name), ("marketplace_seller_id", "=", seller.id),
                                                                   ("picking_type_id", "=", self.env["stock.picking.type"].search([("name", "=", 'Delivery Orders')]).id )])
                for sp_line in spicking_obj:
                    if sp_line.state == "done":
                        total_commission_payment += abs(sol_line.admin_commission)
            
            seller_payment_objs = self.env["seller.payment"].search([("seller_id", "=", seller.id), ("state", "not in",["draft", "requested"]),
                                                                     ('create_date', '>=', start_date), ('create_date', '<=', end_date)])
            for seller_payment in seller_payment_objs:
                #Calculate total marketplace payment for seller
                if seller_payment.state == 'confirm' and seller_payment.payment_mode == "order_paid":
                    total_mp_payment += abs(seller_payment.payable_amount)

                if seller_payment.state == 'posted' and seller_payment.payment_mode == "received_from_seller":
                    total_mp_payment += abs(seller_payment.payable_amount)

                #Calculate total paid marketplace payment for seller
                if seller_payment.state == 'posted' and seller_payment.payment_mode == "seller_payment":
                    paid_mp_payment += abs(seller_payment.payable_amount)

                if seller_payment.state == 'posted' and seller_payment.payment_mode == "cod_payment":
                    paid_mp_payment += abs(seller_payment.payable_amount)

                #Calculate marketplace cashable payment for seller
                if seller_payment.state == 'confirm' and seller_payment.payment_mode == "order_paid" and seller_payment.is_cashable:
                    cashable_amount += abs(seller_payment.payable_amount)

                #Calculate marketplace cashable payment received from seller
                if seller_payment.state == 'posted' and seller_payment.payment_mode == "received_from_seller":
                    cashable_amount += abs(seller_payment.payable_amount)

            return {
                'total_mp_payment': total_mp_payment,
                'paid_mp_payment': paid_mp_payment,
                'balance_mp_payment': abs(total_mp_payment) - abs(paid_mp_payment),
                'total_commission_payment': total_commission_payment,
                }


class MarketplaceOrderResult(models.TransientModel):
    _name = 'mp.commission.result'
    
    start_date = fields.Date('From Date')
    end_date = fields.Date('To Date')  
    report_date = fields.Date('Report Date', default=datetime.today())
      
    mp_seller_name = fields.Char('Seller')
    
    mp_commission_amount = fields.Float('Commission Amount')
    mp_total_mp_payment = fields.Float('Total MP Payment')
    mp_paid_mp_payment = fields.Float('Paid MP Payment')
    mp_balance_mp_payment = fields.Float('Balance MP payment')


# -*- coding: utf-8 -*-

from odoo import fields, models, api, _
from datetime import datetime


class DeliveryPayment(models.Model):
    _name = 'delivery.payment'
    _description = 'Delivery Payment'
          
        
    name = fields.Char('Reference', default='New', readonly=True, copy=False, index=True)
    #mp_orders = fields.Many2many('stock.picking', 'delivery_payment_picking_rel',  string='Marketplace Orders', required=True)
    total_amount = fields.Float('Amount', store=True)
    #receivable_amount = fields.Float('Receivable Amount', readonly=True)
    vendor_id = fields.Many2one('res.partner', 'Delivery Vendor', domain=[('delivery_vendor', '=', True)], ondelete='cascade', required=True)
    pay_date = fields.Date('Payment Date', required=True, default=datetime.now())
    memo = fields.Text('Memo', store=True)
    payment_state = fields.Selection([
        ('draft', 'Draft'),
        ('confirm', 'Confirm'),
        ('done', 'Done')],
        'Payment State', default='draft')
    #required_condition = fields.Boolean('Condition', default=False, readonly=True)
    payment_method = fields.Many2one("delivery.payment.method", string="Payment Method",
                                     help="Payment method in which mode you want payment from vendor.", copy=False)
    payment_mode = fields.Selection([('order_paid', 'Order Paid - COD'), ('delivery_payment', 'Delivery Payment - Prepaid')], string="Payment Mode", required=True, 
                                    default="delivery_payment", readonly=True, states={'draft': [('readonly', False)]}, copy=False)
    description = fields.Text(string="Payment Description",  translate=True, copy=False)
    acc_payment_id = fields.Many2one("account.payment", string="Account Payment", readonly=True, copy=False)
    
        
    def post_payment(self):
        name = self.name
        amount_total = self.total_amount
        pay_date = self.pay_date
        journal_id = int(self.env['ir.config_parameter'].sudo().get_param('picking_and_delivery_vendor.journal_id'))
        vals = {
            'payment_type' : 'inbound',
            'partner_type' : 'supplier',
            'partner_id' : self.vendor_id.id,
            'amount' : amount_total,
            'payment_date' : pay_date,
            'communication' : name,
            'journal_id' : journal_id,
            'currency_id' : self.env.user.company_id.currency_id.id,
            'payment_method_id' : '1',    
        }
        acc_payment_id = self.env['account.payment'].sudo().create(vals)                            
        if acc_payment_id:
            self.write({
                'payment_state': 'confirm',
                'acc_payment_id': acc_payment_id.id,
            })
        
        #for each in self.mp_orders:
        #    lines = each.mapped('sale_id.order_line').filtered(lambda lines: lines.marketplace_seller_id.id == each.marketplace_seller_id.id)
        #    if lines:
        #        lines.write({
        #            'is_paid': True,
        #        })
                

    #@api.onchange('total_amount')
    #def _onchange_total_amount(self):
    #    self.ensure_one()
    #    receivable_amount = self.receivable_amount
    #    total_amount = self.total_amount
    #    
    #    if receivable_amount > total_amount > 0:
    #        self.required_condition = True
    #    else:
    #        self.required_condition = False
    
    #@api.onchange('vendor_id') 
    #def onchange_vendor(self):
    #    journal_id = int(self.env['ir.config_parameter'].sudo().get_param('picking_and_delivery_vendor.journal_id'))  
    #    self.ensure_one()      
    #    domain = []
    #    if self.vendor_id:
    #        domain.append(('vendor_id', '=', self.vendor_id.id))
    #        domain.append(('journal_id', '=', journal_id))   
    #        account_state = self.env['account.move'].search([('invoice_payment_state','=','paid')]) 
    #        print(account_state)
    #        if self.payment_state == 'draft':
    #            for acc_state in account_state:                
    #                self.write({
    #                    'mp_orders': self.env['stock.picking'].search([('vendor_id', '=', self.vendor_id.id), ('journal_id', '=', journal_id),('origin', '=', acc_state.invoice_origin)]),
    #                    'receivable_amount': -(self.vendor_id.debit), 
    #                })
    #    return {'domain': {'mp_orders': domain}}
        
    def done_payment(self):        
        acc_payment_obj = self.env['account.payment'].search([("id", "=", self.acc_payment_id.id)])                                            
        acc_payment_obj.sudo().post()
        if acc_payment_obj.state == "posted":
            self.write({
                'payment_state': 'done',
            })

    @api.model
    def create(self, vals):
        vals['name'] = self.env['ir.sequence'].next_by_code('delivery.payment.seq') or 'New'
        result = super(DeliveryPayment, self).create(vals)
        return result
    
    
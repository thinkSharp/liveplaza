# -*- coding: utf-8 -*-

from odoo import fields, models, api, _
from datetime import datetime, timedelta
from odoo.exceptions import except_orm, Warning, RedirectWarning
from odoo.exceptions import UserError, ValidationError


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    vendor_id = fields.Many2one(
        'res.partner', string='Delivery Vendor', ondelete='cascade')
    delivery_method_id = fields.Many2one(
        'delivery.method', string='Delivery Zone', ondelete='cascade')
    is_picked = fields.Boolean(
        'Picked', default=False)
    is_packaged = fields.Boolean(
        'Packaged', default=False)
    payment_upload = fields.Binary(string='Upload Payment')
    payment_upload_name = fields.Char(string='Upload Payment')
    hold_state = fields.Boolean('Hold State', default=False)
    hold_date = fields.Datetime('Hold Date', store=True)
    hold_reason = fields.Char('Hold Reason', store=True)
    journal_id = fields.Many2one('account.journal', string='Journal', ondelete='cascade',  domain="[('type', 'in', ('bank', 'cash')), ('company_id', '=', company_id)]")
    paid_amount = fields.Float('Paid Amount', store=True)
    receivable_amount = fields.Float('Receivable Amount', compute='_compute_receivable')
    payment_remark = fields.Text('Remark for Payment', store=True, copy=False)
    required_condition = fields.Boolean('Condition', default=False, readonly=True)
    delivery_payment_id = fields.Many2one('delivery.payment', 'Delivery Payment', ondelete='cascade')    
    origin = fields.Char(
        'Order Number', index=True,
        states={'done': [('readonly', True)], 'cancel': [('readonly', True)]},
        help="Reference of the document") 
    
    scheduled_date = fields.Datetime(
        'Scheduled Date', compute='_compute_scheduled_date', inverse='_set_scheduled_date', store=True,
        index=True, default=fields.Datetime.now, tracking=True,
        states={'done': [('readonly', True)], 'cancel': [('readonly', True)]},
        help="Scheduled time for the first part of the shipment to be processed. Setting manually a value here would set it as expected date for all the stock moves.")
    
    @api.onchange('scheduled_date')
    def _onchange_scheduled_date(self):
        next_date = datetime.now() + timedelta(days=21)
        previous_date = datetime.now() - timedelta(days=21)
        if datetime.now() <= next_date or datetime.now() >= previous_date:            
            raise UserError('Your delivery time is more than 21 days ahead. Please check.')
    
    
    @api.onchange('paid_amount')
    def _onchange_paid_amount(self):
        self.ensure_one()
        receivable_amount = self.receivable_amount
        paid_amount = self.paid_amount
        
        if receivable_amount > paid_amount > 0:
            self.required_condition = True
        else:
            self.required_condition = False                                                                                      
    
    def set_as_hold(self):
        self.write({
            'hold_state': True,
            'hold_date': datetime.now(),
        })
    
    def make_ready(self):
        self.write({
            'hold_state': False,
        })

    @api.depends('sale_id.is_picked')
    def is_deli_picked(self):
        self.is_picked = self.sale_id.is_picked
        
    @api.depends('sale_id.is_packaged')
    def is_deli_packaged(self):
        self.is_packaged = self.sale_id.is_packaged
        
    def _compute_receivable(self):

        lines = self.mapped('sale_id.order_line').filtered(lambda lines: lines.marketplace_seller_id.id == self.marketplace_seller_id.id)
        delivery_amount = 0.0
        receivable_amount = 0.0
        if lines:
            payments = self.env['account.move'].search([('ref', '=', self.sale_id.name)])            
            delivery_domain = [('order_id', '=', self.sale_id.id), ('is_delivery', '=', True)]
            delivery_line = self.env['sale.order.line'].search(delivery_domain)            
            
            if delivery_line:
                delivery_amount = delivery_line.price_subtotal                        
            
            for line in lines:
                receivable_amount += line.price_subtotal
                
            if not payments:
                self.write({
                    'receivable_amount': receivable_amount + delivery_amount,
                })
            else:
                self.write({
                    'receivable_amount': receivable_amount,
                })
    
    @api.onchange('journal_id')
    def _onchange_journal_id(self):
        journal_id = self.env['ir.config_parameter'].sudo().get_param('picking_and_delivery_vendor.journal_id')
        if self.journal_id.id == journal_id:
            raise Warning(_("Choose Delivery Vendor."))
    
    
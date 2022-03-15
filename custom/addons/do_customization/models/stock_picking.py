# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from ast import literal_eval
from datetime import date
from datetime import datetime, timedelta
from itertools import groupby
from operator import itemgetter
import time

from odoo import api, fields, models, SUPERUSER_ID, _
from odoo.osv import expression
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
from odoo.tools.float_utils import float_compare, float_is_zero, float_round
from odoo.exceptions import UserError
from odoo.addons.stock.models.stock_move import PROCUREMENT_PRIORITIES


class Picking(models.Model):
    _inherit = "stock.picking"

    payment_provider = fields.Selection(selection=[('manual', 'Custom Payment Form'),('transfer', 'Prepaid'),
                                                    ('cash_on_delivery', 'COD')], string='Payment Type')
    
    is_admin_approved = fields.Boolean('Admin Approved', default=False) 
    
    is_seller_approved = fields.Boolean('Seller Approved', default=False)
    
    township_id = fields.Many2one('res.country.township', related="marketplace_seller_id.township_id",  string="Township", readonly=False, store=True)
    
    state_id = fields.Many2one('res.country.state', related="marketplace_seller_id.state_id", string="State", readonly=False, store=True)
    
    street = fields.Char(related="marketplace_seller_id.street", string="Street", readonly=False, store=True)
    
    buyer_township_id = fields.Many2one('res.country.township', related="partner_id.township_id", string="Township", readonly=False, store=True)
    
    buyer_state_id = fields.Many2one('res.country.state', related="partner_id.state_id", string="State", readonly=False, store=True)
    
    buyer_street = fields.Char(related="partner_id.street", string="Street", readonly=False, store=True)    
    
    buyer_street2 = fields.Char(related="partner_id.street2", string="Street", readonly=False, store=True)
    
    picking_method_id = fields.Many2one('picking.method', string='Pickup Zone', ondelete='cascade')
    
    delivery_person_id = fields.Many2one('res.partner', states={'draft': [('readonly', False)]},
            domain="['|', ('company_type', '=', 'individual'), ('delivery_vendor', '=', True)]", string='Delivery Person') 
    
    pickup_person_id = fields.Many2one('res.partner', states={'draft': [('readonly', False)]},
            domain="['|', ('company_type', '=', 'individual'), ('picking_vendor', '=', True)]", string='Pickup Person') 
    
    state = fields.Selection([
            ('draft', 'Draft'),
            ('waiting', 'Waiting Another Operation'),
            ('confirmed', 'Waiting'),
            ('assigned', 'Ready'),            
            ('done', 'Done'),
            ('cancel', 'Cancelled'),
            ('hold', 'Hold'),
        ], string='Status', compute='_compute_state',
            copy=False, index=True, readonly=True, store=True, tracking=True)
    
    old_state = fields.Char(string="Old Status", readonly=True, store=True)
    
    def do_hold(self):
        if self.state == 'hold':
            self.write({'state': self.old_state, 'old_state': ''})            
        else:
            self.write({'state': 'hold', 'old_state': self.state, 'hold_date': datetime.now()})    
    
    
    
    
    
    
    
    
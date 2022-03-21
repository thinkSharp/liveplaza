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
    
    ready_to_pick = fields.Boolean('Ready to Pick', default=False)
    
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
    
    pick_date = fields.Datetime('Pick Date', store=True)
    pack_date = fields.Datetime('Pack Date', store=True)
    delivery_date = fields.Datetime('Delivery Date', store=True)
    
    def do_hold(self):
        if self.state == 'hold':
            self.write({'state': self.old_state, 'old_state': ''})            
        else:
            self.write({'state': 'hold', 'old_state': self.state, 'hold_date': datetime.now()})    
    
    def action_done(self):
        """Changes picking state to done by processing the Stock Moves of the Picking

        Normally that happens when the button "Done" is pressed on a Picking view.
        @return: True
        """
        self._check_company()

        todo_moves = self.mapped('move_lines').filtered(lambda self: self.state in ['draft', 'waiting', 'partially_available', 'assigned', 'confirmed'])
        # Check if there are ops not linked to moves yet
        for pick in self:
            if pick.owner_id:
                pick.move_lines.write({'restrict_partner_id': pick.owner_id.id})
                pick.move_line_ids.write({'owner_id': pick.owner_id.id})

            # # Explode manually added packages
            # for ops in pick.move_line_ids.filtered(lambda x: not x.move_id and not x.product_id):
            #     for quant in ops.package_id.quant_ids: #Or use get_content for multiple levels
            #         self.move_line_ids.create({'product_id': quant.product_id.id,
            #                                    'package_id': quant.package_id.id,
            #                                    'result_package_id': ops.result_package_id,
            #                                    'lot_id': quant.lot_id.id,
            #                                    'owner_id': quant.owner_id.id,
            #                                    'product_uom_id': quant.product_id.uom_id.id,
            #                                    'product_qty': quant.qty,
            #                                    'qty_done': quant.qty,
            #                                    'location_id': quant.location_id.id, # Could be ops too
            #                                    'location_dest_id': ops.location_dest_id.id,
            #                                    'picking_id': pick.id
            #                                    }) # Might change first element
            # # Link existing moves or add moves when no one is related
            for ops in pick.move_line_ids.filtered(lambda x: not x.move_id):
                # Search move with this product
                moves = pick.move_lines.filtered(lambda x: x.product_id == ops.product_id)
                moves = sorted(moves, key=lambda m: m.quantity_done < m.product_qty, reverse=True)
                if moves:
                    ops.move_id = moves[0].id
                else:
                    new_move = self.env['stock.move'].create({
                                                    'name': _('New Move:') + ops.product_id.display_name,
                                                    'product_id': ops.product_id.id,
                                                    'product_uom_qty': ops.qty_done,
                                                    'product_uom': ops.product_uom_id.id,
                                                    'description_picking': ops.description_picking,
                                                    'location_id': pick.location_id.id,
                                                    'location_dest_id': pick.location_dest_id.id,
                                                    'picking_id': pick.id,
                                                    'picking_type_id': pick.picking_type_id.id,
                                                    'restrict_partner_id': pick.owner_id.id,
                                                    'company_id': pick.company_id.id,
                                                   })
                    ops.move_id = new_move.id
                    new_move._action_confirm()
                    todo_moves |= new_move
                    #'qty_done': ops.qty_done})
        todo_moves._action_done(cancel_backorder=self.env.context.get('cancel_backorder'))
        self.write({'date_done': fields.Datetime.now()})
        
        if self.picking_type_id.name == 'Pick':
            self.write({'pick_date': fields.Datetime.now()})
        elif self.picking_type_id.name == 'Pack':
            self.write({'pack_date': fields.Datetime.now()})
        elif self.picking_type_id.name == 'Delivery Orders':
            self.write({'delivery_date': fields.Datetime.now()})
            
        self._send_confirmation_email()
        return True
    
    @api.onchange('scheduled_date')
    def _onchange_scheduled_date(self):
        next_date = datetime.now() + timedelta(days=21)
        previous_date = datetime.now() - timedelta(days=21)
        if datetime.now() <= next_date or datetime.now() >= previous_date:            
            raise UserError('Your delivery time is more than 21 days ahead. Please check.')
    
    
    
    
    
# -*- coding: utf-8 -*-

from odoo import fields, models, api, _
from datetime import datetime
from odoo.exceptions import except_orm, Warning, RedirectWarning
from odoo.exceptions import UserError, ValidationError
import json

class PickingMethod(models.Model):
    _name = 'picking.method'
    _description = 'Picking Zone'

    name = fields.Char(string='Name', store=True, required=True,
                       copy=False, index=True)
    picking_price = fields.Float(
        string='Price', store=True, copy=False, index=False)
    active = fields.Boolean('Active', default=True)
    related_partner_ids = fields.Many2many(
        'res.partner', 'partner_pickup_rel', string='Partner', readonly=True)
    township_ids = fields.Many2many(
        'res.country.township', 'pkup_tshp_rel', string='Allowed Townships')
    last_used_sequence = fields.Float(string="Last Used Sequence", default=0)
    pickup_vendor_company = fields.Many2one('res.partner', required=True, string='Pickup Vendor Company')
    picking_vendor_domain = fields.Char(compute="_compute_picking_vendor_domain", readonly=True, store=False)

    @api.depends('name')
    def _compute_picking_vendor_domain(self):
        for rec in self:
            user_obj = self.env['res.users'].sudo().browse(rec._uid)
            united_list = []
            if user_obj.partner_id and user_obj.partner_id.is_default:
                if not user_obj.has_group('base.group_system'):
                    for b_id in user_obj.partner_id:
                        united_list.append(b_id.id)
                else:
                    all_vendor_ids = self.env['res.partner'].search([('is_default', '=', True),('delivery_vendor', '=', True),
                                                                   ('picking_vendor', '=', True), ('active', '=', True)])
                    if all_vendor_ids:
                        for v_id in all_vendor_ids:
                            united_list.append(v_id.id)
            else:
                all_vendor_ids = self.env['res.partner'].search(
                    [('is_default', '=', True), ('delivery_vendor', '=', True),
                     ('picking_vendor', '=', True), ('active', '=', True)])
                if all_vendor_ids:
                    for v_id in all_vendor_ids:
                        united_list.append(v_id.id)
            rec.picking_vendor_domain = json.dumps([('id', 'in', united_list)])

    @api.model
    def create(self, vals):
        township_obj = self.env['res.country.township']
        if vals.get("township_ids", False):
            township_obj = self.env['res.country.township'].search([('id', 'in', vals.get("township_ids")[0][2])])
        if vals.get("pickup_vendor_company", False):
            partner_obj = self.env['picking.method'].search([('pickup_vendor_company', '=', vals.get("pickup_vendor_company"))])
            if partner_obj and township_obj:
                for town_data in township_obj:
                    if town_data in partner_obj.township_ids:
                        raise UserError(_(" %s Township is already configured in %s Zone. Please select another township for this Zone.") % (town_data.name, partner_obj.name))
        return super(PickingMethod, self).create(vals)

    def write(self, vals):
        township_obj = self.env['res.country.township']
        if vals.get("township_ids", False):
            township_obj = self.env['res.country.township'].search([('id', 'in', vals.get("township_ids")[0][2])])
        if self.pickup_vendor_company:
            partner_obj = self.env['picking.method'].search([('pickup_vendor_company', '=', self.pickup_vendor_company.id),('id', '!=', self.id)])
            if partner_obj and township_obj:
                for town_data in township_obj:
                    for picking_M in partner_obj:
                        if town_data in picking_M.township_ids:
                            raise UserError(_(" %s Township is already configured in %s Zone. Please select another township for this Zone.") % (town_data.name, picking_M.name))
        return super(PickingMethod, self).write(vals)

class PickingMove(models.Model):
    _name = 'picking.move'
    _description = 'Picking Move'
    _order = "origin DESC"

    name = fields.Char(string='Reference', store=True, required=True,
                       copy=False, index=True, default='New')
    scheduled_date = fields.Datetime(
        string='Scheduled Date', store=True, required=True)
    done_date = fields.Datetime(string='Effective Date', store=True)
    mp_order_id = fields.Many2one(
        'sale.order.line', string='Marketplace Order', ondelete='cascade')
    picking_address = fields.Many2one(
        'res.partner', string='Seller', ondelete='cascade')
    origin = fields.Char(string='Order Number', store=True)
    state = fields.Selection(
        [('draft', 'Draft'), ('pick', 'Picked'), ('cancel', 'Cancelled')], 'State', default='draft')
    vendor_id = fields.Many2one(
        'res.partner', string='Vendor',  ondelete='cascade')
    picking_method_id = fields.Many2one(
        'picking.method', string='Pickup Zone', ondelete='cascade')
    is_ready = fields.Boolean('Ready to Pick', default=False)
    
    township_id = fields.Many2one('res.country.township',
        related="picking_address.township_id",
        string="Township", readonly=False, store=True)
    
    state_id = fields.Many2one('res.country.state',
        related="picking_address.state_id",
        string="State", readonly=False, store=True)
    
    street = fields.Char(
        related="picking_address.street",
        string="Street", readonly=False, store=True)

    def create(self, vals):
        vals['name'] = self.env['ir.sequence'].next_by_code(
            'picking.move.seq') or 'New'
        result = super(PickingMove, self).create(vals)

        return result

    def action_pick(self):
        mp_order = self.mp_order_id
        marketplace_seller_id = self.picking_address
        if mp_order:
            mp_order.write({
                'is_picked': True,
            })

        delivery_record = self.env['stock.picking'].search(
            [('sale_id', '=', mp_order.order_id.id), ('marketplace_seller_id', '=', marketplace_seller_id.id)])
        packaging_record = self.env['packaging.move'].search(
            [('mp_order_id', '=', mp_order.id), ('marketplace_seller_id', '=', marketplace_seller_id.id)])    

        if delivery_record:
            delivery_record.write({
                'is_picked': True,
            })
            
        if packaging_record:
            packaging_record.write({
                'is_picked': True,
            })

        self.write({
            'state': 'pick',
            'done_date': datetime.now(),
        })
        
        
class PackagingMove(models.Model):
    _name = 'packaging.move'
    _description = 'Packaging Move'

    name = fields.Char(string='Reference', store=True, required=True,
                       copy=False, index=True, default='New')
    scheduled_date = fields.Datetime(
        string='Scheduled Date', store=True, required=True)
    done_date = fields.Datetime(string='Effective Date', store=True)
    mp_order_id = fields.Many2one(
        'sale.order.line', string='Marketplace Order', ondelete='cascade')
    origin = fields.Char(string='Order Number', store=True)
    state = fields.Selection(
        [('draft', 'Draft'), ('package', 'Packaged'), ('cancel', 'Cancelled')], 'State', default='draft')
    vendor_id = fields.Many2one(
        'res.partner', string='Vendor',  ondelete='cascade')
    marketplace_seller_id = fields.Many2one('res.partner', string='Seller', ondelete='cascade')
    is_picked = fields.Boolean('Picked', default=False)
    
#     buyer_id = fields.Many2one(
#         'res.partner', string='Buyer',  ondelete='cascade')
    buyer_id = fields.Many2one('res.partner',
        related="mp_order_id.order_partner_id",
        string="Buyer", readonly=False, store=True)
    
    def create(self, vals):
        vals['name'] = self.env['ir.sequence'].next_by_code(
            'packaging.move.seq') or 'New'
        result = super(PackagingMove, self).create(vals)

        return result

    def action_package(self):
        mp_order = self.mp_order_id
        if mp_order:
            mp_order.write({
                'is_packaged': True,
            })

        delivery_record = self.env['stock.picking'].search(
            [('sale_id', '=', mp_order.order_id.id), ('marketplace_seller_id', '=', self.marketplace_seller_id.id)])

        if delivery_record:
            delivery_record.write({
                'is_packaged': True,
            })

        self.write({
            'state': 'package',
            'done_date': datetime.now(),
        })
        
        
        

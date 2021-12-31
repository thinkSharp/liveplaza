# -*- coding: utf-8 -*-

from odoo import fields, models, api, _
from datetime import datetime


class PickingMethod(models.Model):
    _name = 'picking.method'
    _description = 'Picking Zone'

    name = fields.Char(string='Name', store=True, required=True,
                       copy=False, index=True)
    picking_price = fields.Float(
        string='Price', store=True, copy=False, index=False)
    active = fields.Boolean('Active', default=True)
    related_partner_ids = fields.Many2many(
        'res.partner', 'partner_pickup_rel', string='Partner', required=True)
    township_ids = fields.Many2many(
        'res.country.township', 'pkup_tshp_rel', string='Allowed Townships')


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
        'res.partner', string='Address for Picking', ondelete='cascade')
    origin = fields.Char(string='Order Number', store=True)
    state = fields.Selection(
        [('draft', 'Draft'), ('pick', 'Picked'), ('cancel', 'Cancelled')], 'State', default='draft')
    vendor_id = fields.Many2one(
        'res.partner', string='Vendor',  ondelete='cascade')
    picking_method_id = fields.Many2one(
        'picking.method', string='Pickup Zone', ondelete='cascade')
    is_ready = fields.Boolean('Ready to Pick', default=False)

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
    origin = fields.Char(string='Source Document', store=True)
    state = fields.Selection(
        [('draft', 'Draft'), ('package', 'Packaged'), ('cancel', 'Cancelled')], 'State', default='draft')
    vendor_id = fields.Many2one(
        'res.partner', string='Vendor',  ondelete='cascade')
    marketplace_seller_id = fields.Many2one('res.partner', string='Seller', ondelete='cascade')
    is_picked = fields.Boolean('Picked', default=False)
    
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
        
        
        

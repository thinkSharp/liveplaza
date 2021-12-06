# -*- coding: utf-8 -*-

from odoo import fields, models, api, _


class ResPartner(models.Model):
	_inherit = 'res.partner'

	picking_vendor = fields.Boolean('Picking Vendor', default=False)
	picking_method_ids = fields.Many2many(
		'picking.method', 'partner_pickup_rel', string='Picking Zone')
	delivery_vendor = fields.Boolean('Delivery Vendor', default=False)
	delivery_method_ids = fields.Many2many(
		'delivery.method', 'partner_deli_rel', string='Delivery Zone')
	vendor_sequence = fields.Integer(string="Sequence", store=True)
	active_delivery = fields.Boolean('Active Delivery', default=False)
 
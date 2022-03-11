# -*- coding: utf-8 -*-

from odoo import fields, models, api, _
#from bokeh.themes import default
import json

class ResPartner(models.Model):
	_inherit = 'res.partner'

	picking_vendor = fields.Boolean('Picking Vendor', default=False)
	picking_method_ids = fields.Many2many(
		'picking.method', 'partner_pickup_rel', string='Picking Zone', domain=[("active", "=", True)])
	delivery_vendor = fields.Boolean('Delivery Vendor', default=False)
	delivery_method_ids = fields.Many2many(
		'delivery.method', 'partner_deli_rel', string='Delivery Zone', domain=[("active", "=", True)])
	vendor_sequence = fields.Integer(string="Sequence", store=True)
	active_delivery = fields.Boolean('Active Delivery', default=False)
	delivery_method_domain = fields.Char(compute="_compute_delivery_domain", readonly=True, store=False,)
	picking_method_domain = fields.Char(compute="_compute_picking_domain", readonly=True, store=False,)
	

	@api.depends('parent_id','company_type')
	def _compute_delivery_domain(self):
		for rec in self:
			dm_list = []
			if rec.parent_id:
				if rec.company_type == 'person':
					for dm_id in rec.parent_id.delivery_method_ids:
						dm_list.append(dm_id.id)
					rec.delivery_method_domain = json.dumps([('id', 'in', dm_list)] )
				else:
					dm_objs = self.env['delivery.method'].search([])
					for dm_id in dm_objs:
						dm_list.append(dm_id.id)
					rec.delivery_method_domain = json.dumps([('id', 'in', dm_list)] )	
			else:
				dm_objs = self.env['delivery.method'].search([])
				for dm_id in dm_objs:
					dm_list.append(dm_id.id)
				rec.delivery_method_domain = json.dumps([('id', 'in', dm_list)] )					
				
				
	@api.depends('parent_id','company_type')
	def _compute_picking_domain(self):
		for rec in self:
			pm_list = []
			if rec.parent_id:				
				if rec.company_type == 'person':
					for pm_id in rec.parent_id.picking_method_ids:
						pm_list.append(pm_id.id)
					rec.picking_method_domain = json.dumps([('id', 'in', pm_list)] )
				else:
					pm_objs = self.env['picking.method'].search([])
					for pm_id in pm_objs:
						pm_list.append(pm_id.id)
					rec.picking_method_domain = json.dumps([('id', 'in', pm_list)] )
			else:
				pm_objs = self.env['picking.method'].search([])
				for pm_id in pm_objs:
					pm_list.append(pm_id.id)
				rec.picking_method_domain = json.dumps([('id', 'in', pm_list)] )
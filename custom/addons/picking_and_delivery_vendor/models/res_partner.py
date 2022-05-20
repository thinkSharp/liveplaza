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
	delivery_payable_by_company = fields.Monetary(string="Total Amount", readonly=True, compute="_calculate_delivery_payment", currency_field='seller_currency_id')
	total_mp_payable_by_vendor = fields.Monetary(string="Total Amount",  readonly=True,
								compute="_calculate_delivery_payment", currency_field='seller_currency_id') #total payment from delivery vendor to liveplaza company
	deli_com_paid = fields.Monetary(string="Paid Amount", readonly=True, compute="_calculate_delivery_payment", currency_field='seller_currency_id')
	mp_vendor_paid = fields.Monetary(string="Paid Amount", readonly=True, compute="_calculate_delivery_payment", currency_field='seller_currency_id')
	deli_com_balance = fields.Monetary(string="Balance Amount", readonly=True, compute="_calculate_delivery_payment", currency_field='seller_currency_id')
	mp_vendor_balance = fields.Monetary(string="Balance Amount", readonly=True, compute="_calculate_delivery_payment", currency_field='seller_currency_id')
            
          
                
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

	def _calculate_delivery_payment(self):	   
		for obj in self:
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
						
				obj.total_mp_payable_by_vendor = total_mp_payable_by_vendor
				obj.delivery_payable_by_company = delivery_payable_by_company
				obj.deli_com_paid = deli_com_paid
				obj.mp_vendor_paid = mp_vendor_paid
				obj.deli_com_balance = abs(delivery_payable_by_company - deli_com_paid)
				obj.mp_vendor_balance = abs(total_mp_payable_by_vendor - mp_vendor_paid)
			else:
				obj.total_mp_payable_by_vendor = 0.0
				obj.delivery_payable_by_company = 0.0 
				obj.deli_com_paid = 0.0
				obj.mp_vendor_paid = 0.0
				obj.deli_com_balance = 0.0
				obj.mp_vendor_balance =  0.0
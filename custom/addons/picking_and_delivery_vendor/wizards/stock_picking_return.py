# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from datetime import datetime


class ReturnPicking(models.TransientModel):
	_name = 'stock.return.picking'
	_inherit = 'stock.return.picking'

	def _create_payment_return(self):
		name = self.picking_id.sale_id.display_name
		amount_total = self.picking_id.paid_amount
		
		if self.picking_id.journal_id.id == 25:
			# LiveP to Delivery Vendor
			livep_cash_move = {
				'name': name,
				'account_id': self.picking_id.journal_id.default_credit_account_id.id,
				'debit':  0.0,	
				'credit':  amount_total or 0.0,
			}

			delivery_vendor_payable = {
				'name': name,
				'account_id': self.picking_id.vendor_id.property_account_payable_id.id,
				'debit':  amount_total or 0.0,
				'credit': 0.0,
				'partner_id' : self.picking_id.vendor_id.id,
			}
					
			livep_move_vals = {
				'ref': _("Refund Payment of %s") % name,
				'date': datetime.now(),
				'journal_id': 25,
				'line_ids': [(0, 0, livep_cash_move),(0, 0, delivery_vendor_payable)],
			}
		
			self.env['account.move'].sudo().create(livep_move_vals)
   
			# Delivery Vendor to Buyer
			delivery_vendor_move = {
				'name': name,
				'account_id': self.picking_id.vendor_id.property_account_payable_id.id,
				'debit':  0.0,	
				'credit':  amount_total or 0.0,
				'partner_id' : self.picking_id.vendor_id.id,
			}

			buyer_move = {
				'name': name,
				'account_id': self.picking_id.sale_id.partner_invoice_id.property_account_receivable_id.id,
				'debit':  amount_total or 0.0,
				'credit': 0.0,
				'partner_id' : self.picking_id.sale_id.partner_invoice_id.id,
			}
					
			delivery_move_vals = {
				'ref': _("Refund Payment of %s") % name,
				'date': datetime.now(),
				'journal_id': 26,
				'line_ids': [(0, 0, delivery_vendor_move),(0, 0, buyer_move)],
			}
		
			self.env['account.move'].sudo().create(delivery_move_vals)
   
		else:
			vals = {
				'payment_type' : 'outbound',
				'partner_type' : 'customer',
				'partner_id' : self.picking_id.sale_id.partner_invoice_id.id,
				'amount' : amount_total,
				'payment_date' : datetime.now(),
				'communication' : _("Refund Payment of %s") % name,
				'journal_id' : self.picking_id.journal_id.id,
				'currency_id' : 119,
				'payment_method_id' : '1',    
			}
												
			self.env['account.payment'].sudo().create(vals)


	def create_returns(self):
		for wizard in self:
			new_picking_id, pick_type_id = wizard._create_returns()
			wizard._create_payment_return()
		# Override the context to disable all the potential filters that could have been set previously
		ctx = dict(self.env.context)
		ctx.update({
			'default_partner_id': self.picking_id.partner_id.id,
			'search_default_picking_type_id': pick_type_id,
			'search_default_draft': False,
			'search_default_assigned': False,
			'search_default_confirmed': False,
			'search_default_ready': False,
			'search_default_late': False,
			'search_default_available': False,
		})
		return {
			'name': _('Returned Picking'),
			'view_mode': 'form,tree,calendar',
			'res_model': 'stock.picking',
			'res_id': new_picking_id,
			'type': 'ir.actions.act_window',
			'context': ctx,
		}

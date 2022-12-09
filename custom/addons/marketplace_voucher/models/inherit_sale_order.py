# -*- coding: utf-8 -*-
#################################################################################
#
#    Copyright (c) 2015-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>)
#
#################################################################################
from odoo import api, fields, models, _
from odoo import tools
from odoo.exceptions import UserError, ValidationError
from datetime import datetime, timedelta
import logging
_logger = logging.getLogger(__name__)

class sale_order(models.Model):
	_inherit = "sale.order"

	applied_voucher = fields.Many2one("voucher.voucher", "Applied Voucher")

	@api.model
	def _add_voucher(self, wk_order_total , voucher_dict, so_id=False):
		voucher_id = voucher_dict['coupon_id']
		voucher_value = voucher_dict['value']
		voucher_obj = self.env['voucher.voucher'].sudo().browse(voucher_id)
		if not self.ids:
			order_id = so_id
		else:
			order_id = self.ids[0]
		order_obj = self.browse(order_id)
		order_lines = False
		if voucher_obj.marketplace_seller_id:
			order_lines = order_obj.order_line.filtered(lambda l: l.product_id.marketplace_seller_id and
				l.product_id.marketplace_seller_id.id == voucher_obj.marketplace_seller_id.id )
			if order_lines:
				seller_products_amount = sum(order_lines.mapped("price_subtotal"))
				wk_order_total = seller_products_amount

		result = super(sale_order, self)._add_voucher(wk_order_total, voucher_dict, so_id)

		status = result.get("status") and result.get("status").get("status")
		if status and voucher_obj.marketplace_seller_id:
			order_lines = order_obj.order_line.filtered(lambda l: l.product_id.marketplace_seller_id and
				l.product_id.marketplace_seller_id.id == voucher_obj.marketplace_seller_id.id)
			if not order_lines:
				# remove voucher if cart has no products of seller whose voucher is applied
				voucher_product_id = voucher_dict['product_id']
				voucher_prod_line = order_obj._cart_find_product_line(voucher_product_id)
				if voucher_prod_line and not order_lines:
					voucher_prod_line.unlink()
					result['status'] = False
					result['message'] = _('This coupon code is not valid.')
					order_obj.applied_voucher = False
			else:
				order_obj.applied_voucher = voucher_obj.id
		return result

	# add new email template when order is confirmed (add voucher info)
	def _find_mail_template(self, force_confirmation_template=False):
		template_id = False
		if force_confirmation_template or (self.state == 'sale' and not self.env.context.get('proforma', False)):
			template_id = int(self.env['ir.config_parameter'].sudo().get_param('sale.default_confirmation_template'))
			template_id = self.env['mail.template'].search([('id', '=', template_id)]).id
			if not template_id:
				template_id = self.env['ir.model.data'].xmlid_to_res_id(
					'marketplace_voucher.mail_template_sale_confirmation', raise_if_not_found=False)
		if not template_id:
			template_id = self.env['ir.model.data'].xmlid_to_res_id('sale.email_template_edi_sale',
																	raise_if_not_found=False)

		return template_id

	# def write(self, vals):
	# 	res = super(sale_order, self).write(vals)
	# 	applied_voucher = vals.get("applied_voucher") if vals.get("applied_voucher") else self.applied_voucher
	# 	if applied_voucher:
	# 		applied_voucher = self.env['voucher.voucher'].browse(int(applied_voucher))
	# 		if applied_voucher and applied_voucher.marketplace_seller_id:
	# 			voucher_lines = self.order_line.filtered(lambda l: l.product_id.marketplace_seller_id == applied_voucher.marketplace_seller_id)
	# 			# if not voucher_lines:
	# 			# 	raise UserError(_("This voucher code is not valid."))
	# 	return res

class SaleOrderLine(models.Model):
	_inherit = 'sale.order.line'

	def unlink(self):
		product_id = self.env['ir.default'].sudo().get('res.config.settings', 'wk_coupon_product_id')
		for line in self:
			if line.product_id.id == product_id:
				line.order_id.applied_voucher = False
				self.order_id.wk_coupon_value = 0
		return super(SaleOrderLine, self).unlink()

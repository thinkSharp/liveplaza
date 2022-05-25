# -*- coding: utf-8 -*-
#################################################################################
##    Copyright (c) 2018-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>)
#    You should have received a copy of the License along with this program.
#    If not, see <https://store.webkul.com/license.html/>
#################################################################################

from odoo import SUPERUSER_ID
from odoo import http
from odoo.http import request
import datetime
from odoo.addons.website_sale.controllers.main import WebsiteSale
import logging
logger = logging.getLogger(__name__)


class WebsiteDailyDeals(WebsiteSale):

	@http.route(['/daily/deals'], type='http', auth="public", website=True)
	def website_daily_deals(self, **post):
		values={
			'daily_deals': request.env['website.deals'].sudo().get_valid_deals(),
			'page_header':request.env['website.deals'].sudo().get_page_header(),
			'pricelist':request.website.get_current_pricelist(),
			'datetime':datetime,
		}
		return http.request.render("website_daily_deals.daily_deals_page", values)

	@http.route(['/daily/deal/expired/<model("website.deals"):deal>'], type='json', auth="public", website=True)
	def website_deal_expired(self, deal,**post):
		if deal:
			deal.set_to_expired()
		return  deal and deal.state == 'expired'


	# @http.route(['/deal/<model("website.deals"):deal>'], type='http', auth="public", website=True)
	# def individual_deal(self, deal=False ,**post):
	# 	context = request.context or {}
	# 	if not context.get('pricelist'):
	# 		pricelist = self.get_pricelist()
	# 		# context['pricelist'] = int(pricelist)
	# 	else:
	# 		pricelist = request.env['product.pricelist'].sudo().with_context(context).browse(context['pricelist'])
	# 	from_currency = request.env['res.users'].sudo().with_context(context).browse(request.uid).company_id.currency_id
	# 	to_currency = pricelist.currency_id
	# 	compute_currency = lambda price: request.env['res.currency'].sudo().with_context(context)._compute(from_currency, to_currency, price)
	# 	deal = request.env['website.deals'].sudo().with_context(context).browse(deal.id)
	# 	values={
	# 		'pricelist': pricelist,
	# 		'compute_currency': compute_currency,
	# 		'individual_deal':deal
	# 	}
	# 	return http.request.render("website_daily_deals.individual_deal", values)
	# @http.route(['/deals/change_size'], type='json', auth="public")
	# def deals_change_size(self, id, x, y):
	# 	offer_obj = request.env['product.pricelist.item'].sudo().browse(id)
	# 	size = offer_obj.sudo().write({'website_size_x': x, 'website_size_y': y})
	# 	return  size

	# @http.route(['/deal/change_sequence'], type='json', auth="public")
	# def change_sequence(self, id, sequence):
	# 	context = request.context
	# 	offer_obj = request.env['product.pricelist.item'].browse(id)
	# 	if sequence == "top":
	# 		offer_obj.sudo().with_context(context).set_sequence_top()
	# 	elif sequence == "bottom":
	# 		offer_obj.sudo().with_context(context).set_sequence_bottom()
	# 	elif sequence == "up":
	# 		offer_obj.sudo().with_context(context).set_sequence_up()
	# 	elif sequence == "down":
	# 		offer_obj.sudo().with_context(context).set_sequence_down()

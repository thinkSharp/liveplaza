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
from odoo.addons.http_routing.models.ir_http import slug
from odoo.addons.website.controllers.main import QueryURL
from odoo.addons.website_sale.controllers.main import TableCompute


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

	@http.route([
		'''/daily/deals/<model("website.deals"):deal>''',
        '''/daily/deals/<model("website.deals"):deal>/page/<int:page>'''
	], type='http', auth="public", website=True)
	def deal_products(self, deal=None ,page=0, search='', ppg=False, **post):
		if not ppg:
			ppg = request.env['website'].get_current_website().shop_ppg or 20

		PPR = 4

		if ppg:
			try:
				ppg = int(ppg)
			except ValueError:
				ppg = SPG
			post["ppg"] = ppg
		else:
			ppg = SPG

		url = "/daily/deals"
		if deal:
			url = "/daily/deals/%s" % slug(deal)
			items = deal.get_instock_items()
			item_list = []
			for data in items:
				item_list.append(data.id)
			items = request.env['product.pricelist.item'].search([('id', 'in', item_list)])	
        	
		if search:
			post["search"] = search

		product_count = len(items)
		pager = request.website.pager(url=url, total=product_count, page=page, step=ppg, scope=7, url_args=post)
		offset = pager['offset']
		#products = items[offset: offset + ppg]
		products = request.env['product.pricelist.item'].search([('id', 'in', item_list)],limit=ppg, offset=pager['offset'])
		keep = QueryURL(url, order=post.get('order'))

		#########################
		context = request.context or {}
		if not context.get('pricelist'):
			pricelist = request.website.get_current_pricelist()
			# context['pricelist'] = int(pricelist)
		else:
			pricelist = request.env['product.pricelist'].sudo().with_context(context).browse(context['pricelist'])
		from_currency = request.env['res.users'].sudo().with_context(context).browse(request.uid).company_id.currency_id
		to_currency = pricelist.currency_id
		compute_currency = lambda price: request.env['res.currency'].sudo().with_context(context)._compute(from_currency, to_currency, price)
		deal = request.env['website.deals'].sudo().with_context(context).browse(deal.id)
		#########################


		values = {
			'pricelist': pricelist,
			'compute_currency': compute_currency,
			'daily_deals':deal,
			'search': search,
			'pager': pager,
			'products': products,
			'search_count': product_count,  # common for all searchbox
			'bins': TableCompute().process(products, ppg, PPR),
			'ppg': ppg,
			'ppr': PPR,
			'layout_mode': 'grid',
			'keep': keep,
		}
		print(values)
		if values.get("pager").get('page_end').get('num') < page:
			print("none")
			return "none"
		elif post.get("test"):
			print("test")
			view = request.render("website_daily_deals.wk_lazy_list_deals_item", values)
			return view
		else:
			print("else")
			return http.request.render("website_daily_deals.daily_deals_detail_page", values)

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

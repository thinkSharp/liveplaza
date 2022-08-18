# -*- coding: utf-8 -*-
import json
from odoo import http
from odoo.http import request


class WebsiteLivep(http.Controller):
    # @http.route('/website_livep/website_livep/', auth='public')
    # def index(self, **kw):
    #     return "Hello, world"

    # @http.route('/website_livep/website_livep/objects/', auth='public')
    # def list(self, **kw):
    #     return http.request.render('website_livep.listing', {
    #         'root': '/website_livep/website_livep',
    #         'objects': http.request.env['website_livep.website_livep'].search([]),
    #     })

    # @http.route('/website_livep/website_livep/objects/<model("website_livep.website_livep"):obj>/', auth='public')
    # def object(self, obj, **kw):
    #     return http.request.render('website_livep.object', {
    #         'object': obj
    #     })

    @http.route('/website_livep/cart/', auth='public', website=True)
    def cart(self, **kw):
      website_sale_order = request.website.sale_get_order()
      return request.render('website_livep.cart', {
        'website_sale_order': website_sale_order,
      })


    @http.route('/website_livep/compare_list/', auth='public', website=True)
    def compare_list(self, product_ids='', **kw):
      if product_ids:
        product_ids = product_ids.split(',')
      else:
        product_ids = []
      
      context = dict(request.env.context)
      pricelist = request.website.get_current_pricelist()
      context.setdefault('pricelist', pricelist)

      products = request.env['product.product'].with_context(context, display_default_code=False).search([('id', 'in', product_ids)])
      return request.render('website_livep.compare_list', {
        'products': products
      })
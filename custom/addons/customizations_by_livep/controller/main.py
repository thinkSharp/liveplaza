# -*- coding: utf-8 -*-

from odoo import fields, http, tools, _
from odoo.http import request

from werkzeug.exceptions import Forbidden, NotFound


from odoo.addons.website_sale.controllers.main import WebsiteSale
from odoo.addons.website.controllers.main import Website
from odoo.exceptions import except_orm, Warning, RedirectWarning, UserError


class WebsiteSale(WebsiteSale):    
    
    def _get_mandatory_billing_fields(self):
        return ["name", "street", "city", "country_id","township_id"]

    def _get_mandatory_shipping_fields(self):
        return ["name", "street", "city", "country_id","township_id"]

    def _get_search_order(self, post):
        order = post.get('order') or 'website_sequence DESC'
#         or 'qty_available ASC'
        return 'is_published desc, %s, id desc' % order
    
#     @http.route(['/shop/address'], type='http', methods=['GET', 'POST'], auth="public", website=True, sitemap=False)
#     def address(self, **kw):
#         if  kw.get("name",False):
#             township_id = kw.get("township_id")
#             if township_id == None:
#                 raise Warning(_("Quantity cannot be negative."))
#             values=super(WebsiteSale,self).address(**kw)
#         return values

    def _checkout_form_save(self, mode, checkout, all_values):
        Partner = request.env['res.partner']

        township_id = all_values.get('township_id')

        checkout.update({'township_id': township_id})

        if mode[0] == 'new':
            partner_id = Partner.sudo().with_context(
                tracking_disable=True).create(checkout).id
        elif mode[0] == 'edit':
            partner_id = int(all_values.get('partner_id', 0))
            if partner_id:
                # double check
                order = request.website.sale_get_order()
                shippings = Partner.sudo().search(
                    [("id", "child_of", order.partner_id.commercial_partner_id.ids)])
                if partner_id not in shippings.mapped('id') and partner_id != order.partner_id.id:
                    return Forbidden()
                Partner.browse(partner_id).sudo().write(checkout)
        return partner_id


class Website(Website):

    @http.route(website=True, auth="public", sitemap=False)
    def web_login(self, redirect=None, *args, **kw):
        response = super(Website, self).web_login(
            redirect=redirect, *args, **kw)
        if not redirect and request.params['login_success']:
            redirect = '/shop'
            return http.redirect_with_hash(redirect)
        return response

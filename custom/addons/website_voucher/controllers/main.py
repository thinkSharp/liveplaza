#  -*- coding: utf-8 -*-
#################################################################################
#
#   Copyright (c) 2019-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>)
#   See LICENSE URL <https://store.webkul.com/license.html/> for full copyright and licensing details.
#################################################################################
from odoo import http
from odoo.http import request
from odoo.tools.translate import _
from odoo.addons.website_sale.controllers.main import WebsiteSale
import logging
from odoo.addons.website_sale.controllers.main import WebsiteSale as Website_Sale
from odoo import fields, http, SUPERUSER_ID, tools, _

_logger = logging.getLogger(__name__)


class website_voucher(http.Controller):

    @http.route('/website/voucher/', type='json', auth="public", methods=['POST'], website=True)
    def voucher_call(self, secret_code=False, change=False):
        try:
            result = {}
            voucher_obj = request.env['voucher.voucher']
            order = request.website.sale_get_order()
            wk_order_total = order.checked_amount_total
            partner_id = request.env['res.users'].browse(request.uid).partner_id.id
            products = []
            for line in order.order_line:
                if line.selected_checkout:
                    products.append(line.product_id.id)
            result = voucher_obj.sudo().validate_voucher(secret_code, wk_order_total, products, refrence="ecommerce",
                                                         partner_id=partner_id)
            if result['status']:
                if change:
                    final_result = request.website.sale_get_order(force_create=1)._change_voucher(wk_order_total, result)
                else:
                    final_result = request.website.sale_get_order(force_create=1)._add_voucher(wk_order_total, result)
                if not final_result['status']:
                    result.update(final_result)
                request.session['secret_key_data'] = {'coupon_id': result['coupon_id'],
                                                      'total_available': result['total_available'],
                                                      'wk_voucher_value': result['value'],
                                                      'voucher_val_type': result['voucher_val_type'],
                                                      'customer_type': result['customer_type']}
            return result
        except Exception as e:
            _logger.info('-------------Exception-----%r', e)

    @http.route(['/voucher/remove'], type='json', auth="public", methods=['POST'], website=True)
    def voucher_remove(self):
        order = request.website.sale_get_order()
        for line in order.order_line:
            if line.is_voucher:
                line.sudo().unlink()
                order.wk_coupon_value = 0
                return request.redirect("/shop/cart/")

    @http.route(['/shop/cart/voucher_remove/<line_id>'], type='http', auth="public", website=True)
    def remove_voucher(self, line_id='0'):
        try:
            voucher_obj = request.env['voucher.voucher']
            product_id = request.env['ir.default'].sudo().get('res.config.settings', 'wk_coupon_product_id')
            if product_id and line_id:
                line_obj = request.env["sale.order.line"].sudo().browse(int(line_id))
                if line_obj.wk_voucher_id:
                    voucher_obj.sudo().return_voucher(line_obj.wk_voucher_id.id, int(line_id), refrence="ecommerce")
                line_obj.price_unit = 0
                line_obj.sudo().unlink()
                request.session['secret_key_data'] = {}
            return request.redirect("/shop/cart/")
        except Exception as e:
            _logger.info('-------------Exception-----%r', e)
            return request.redirect("/shop/cart/")

    # Remove the voucher if there is no product in cart
    @http.route(['/voucher/validate/cart_change'], type='json', auth="public", methods=['POST'], website=True,
                csrf=False)
    def cart_update_voucher(self):
        order = request.website.sale_get_order(force_create=1)
        if len(order.order_line) <= 2:
            for line in order.order_line:
                if line.is_voucher:
                    order.remove_voucher()
                    return True
        return False


class WebsiteSale(Website_Sale):

    # This function is to remove discount after gift voucher is deleted
    @http.route(['/shop/cart/update_json'], type='json', auth="public", methods=['POST'], website=True, csrf=False)
    def cart_update_json(self, product_id, line_id=None, add_qty=None, set_qty=None, display=True):
        """This route is called when changing quantity from the cart or adding
        a product from the wishlist."""
        order = request.website.sale_get_order(force_create=1)
        new_product_id = product_id

        # remove voucher if the related product is deleted from cart
        for line in order.order_line:
            if line.wk_voucher_id:
                check_product = order.check_voucher_product(order, line.wk_voucher_id,
                                                            product_id=new_product_id)
                if not check_product:
                    if not set_qty or set_qty <= 0:
                        line.sudo().unlink()
                    order.wk_coupon_value = 0
        if order.state != 'draft':
            request.website.sale_reset()
            return {}

        value = order._cart_update(product_id=product_id, line_id=line_id, add_qty=add_qty, set_qty=set_qty)

        if not order.cart_quantity:
            request.website.sale_reset()
            return value

        order = request.website.sale_get_order()
        value['cart_quantity'] = order.cart_quantity

        if not display:
            return value

        value['website_sale.cart_lines'] = request.env['ir.ui.view'].render_template("website_sale.cart_lines", {
            'website_sale_order': order,
            'date': fields.Date.today(),
            'suggested_products': order._cart_accessories()
        })
        value['website_sale.short_cart_summary'] = request.env['ir.ui.view'].render_template(
            "website_sale.short_cart_summary", {
                'website_sale_order': order,
            })


        return value

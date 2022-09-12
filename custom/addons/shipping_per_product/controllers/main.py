# -*- coding: utf-8 -*-
#################################################################################
# Author      : Webkul Software Pvt. Ltd. (<https://webkul.com/>)
# Copyright(c): 2015-Present Webkul Software Pvt. Ltd.
# License URL : https://store.webkul.com/license.html/
# All Rights Reserved.
#
#
#
# This program is copyright property of the author mentioned above.
# You can`t redistribute it and/or modify it.
#
#
# You should have received a copy of the License along with this program.
# If not, see <https://store.webkul.com/license.html/>
#################################################################################
from odoo import http, _
from odoo.tools import float_round
from odoo.http import request

import logging
_logger = logging.getLogger(__name__)

class ProductShipping(http.Controller):

    def sol_update_website_sale_delivery_return(self, order, carrier_id, lines):
        Monetary = request.env['ir.qweb.field.monetary']
        if order:
            currency = order.currency_id
            sol_delivery_amount = sum(lines.mapped('delivery_charge'))
            # sol_delivery_amount = float_round(sol_delivery_amount, 2)
            new_total_delivery_amount = order.get_total_sol_delivery_price()
            order.checked_amount_total += new_total_delivery_amount
            # order.amount_total += new_total_delivery_amount

            # new_total_delivery_amount = float_round(new_total_delivery_amount, 2)
            return {
                'status': order.delivery_rating_success,
                'error_message': order.delivery_message,
                'carrier_id': carrier_id,
                'is_free_delivery': not bool(order.amount_delivery),
                'sol_delivery_amount': Monetary.value_to_html(sol_delivery_amount, {'display_currency': currency}),
                'new_amount_delivery': Monetary.value_to_html(new_total_delivery_amount, {'display_currency': currency}),
                'new_amount_untaxed': Monetary.value_to_html(order.checked_amount_untaxed, {'display_currency': currency}),
                'new_amount_tax': Monetary.value_to_html(order.checked_amount_tax, {'display_currency': currency}),
                'new_amount_total': Monetary.value_to_html(order.checked_amount_total, {'display_currency': currency}),
            }
        return {}

    @http.route(['/shop/sol/update_carrier'], type='json', auth='public', methods=['POST'], website=True, csrf=False)
    def update_shop_sol_carrier(self, **post):
        order = request.website.sale_get_order()
        address = order.partner_shipping_id
        carrier_id = int(post['carrier_id'])
        carriers = request.env['delivery.carrier'].sudo().search([('website_published', '=', True)]).available_carriers(address)
        for c in carriers:
            if c.id == carrier_id:
                print(c.name, " = ", carrier_id)
                order.selected_carrier_id = c.id

        order_lines = post.get('order_lines')
        order_lines = request.env["sale.order.line"].sudo().browse(order_lines)
        if order:
            order._check_carrier_sol_quotation(force_carrier_id=carrier_id, lines=order_lines)
        return self.sol_update_website_sale_delivery_return(order, carrier_id, order_lines)

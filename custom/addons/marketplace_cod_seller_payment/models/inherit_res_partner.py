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

from odoo import models, fields, api, _
import decimal,re

import logging
_logger = logging.getLogger(__name__)

class ResPartner(models.Model):
    _inherit = 'res.partner'


    def _calculate_mp_related_payment(self):
        for obj in self:
            if obj.seller:
                total_mp_payment = paid_mp_payment = cashable_amount = total_commission_payment = 0
                
                sol_objs = self.env["sale.order.line"].search([("marketplace_seller_id", "=", obj.id), ("is_delivery", "=", False)])
                picking_type_id = self.env["stock.picking.type"].search([("name", "=", 'Delivery Orders')])
                
                for sol_line in sol_objs:
                    spicking_obj = self.env["stock.picking"].search([("origin", "=", sol_line.order_id.name), ("marketplace_seller_id", "=", obj.id),
                                                                       ("picking_type_id", "=", self.env["stock.picking.type"].search([("name", "=", 'Delivery Orders')]).id )])
                    for sp_line in spicking_obj:
                        if sp_line.state == "done":
                            total_commission_payment += abs(sol_line.admin_commission)
                
                seller_payment_objs = self.env["seller.payment"].search([("seller_id", "=", obj.id), ("state", "not in",["draft", "requested"])])
                for seller_payment in seller_payment_objs:
                    #Calculate total marketplace payment for seller
                    if seller_payment.state == 'confirm' and seller_payment.payment_mode == "order_paid":
                        total_mp_payment += abs(seller_payment.payable_amount)

                    if seller_payment.state == 'posted' and seller_payment.payment_mode == "received_from_seller":
                        total_mp_payment += abs(seller_payment.payable_amount)

                    #Calculate total paid marketplace payment for seller
                    if seller_payment.state == 'posted' and seller_payment.payment_mode == "seller_payment":
                        paid_mp_payment += abs(seller_payment.payable_amount)

                    if seller_payment.state == 'posted' and seller_payment.payment_mode == "cod_payment":
                        paid_mp_payment += abs(seller_payment.payable_amount)

                    #Calculate marketplace cashable payment for seller
                    if seller_payment.state == 'confirm' and seller_payment.payment_mode == "order_paid" and seller_payment.is_cashable:
                        cashable_amount += abs(seller_payment.payable_amount)

                    #Calculate marketplace cashable payment received from seller
                    if seller_payment.state == 'posted' and seller_payment.payment_mode == "received_from_seller":
                        cashable_amount += abs(seller_payment.payable_amount)

                obj.total_mp_payment = total_mp_payment
                obj.paid_mp_payment = paid_mp_payment
                obj.cashable_amount = (round(decimal.Decimal(cashable_amount - obj.paid_mp_payment), 2))

                #Calculate total balanec marketplace payment for seller
                obj.balance_mp_payment = abs(obj.total_mp_payment) - abs(obj.paid_mp_payment)

                #Calculate marketplace available payment for seller
                obj.available_amount = (round(decimal.Decimal(obj.balance_mp_payment), 2))
                obj.total_commission_payment = total_commission_payment
            else:
                obj.total_mp_payment = 0
                obj.paid_mp_payment = 0
                obj.cashable_amount = 0
                obj.balance_mp_payment = 0
                obj.available_amount = 0
                obj.total_commission_payment = total_commission_payment


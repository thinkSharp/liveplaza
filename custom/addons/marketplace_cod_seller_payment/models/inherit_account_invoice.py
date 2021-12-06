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

import logging
_logger = logging.getLogger(__name__)


class AccountMove(models.Model):
    _inherit = 'account.move'

    def mp_post_action_invoice_paid(self):
        res = super(AccountMove, self).mp_post_action_invoice_paid()
        for rec in self:
            if rec.type in ['in_invoice', 'in_refund']:
                seller_payment = self.env["seller.payment"].search(
                    [("invoice_id", "=", rec.id)])
                if seller_payment and seller_payment.payment_mode == "cod_payment" and rec.invoice_payment_state == "paid":
                    seller_payment.write({'state': "posted"})
        return res

    @api.model
    def create_seller_payment_new(self, sellers_dict):
        result = super(AccountMove, self).create_seller_payment_new(sellers_dict)
        invoice_id = sellers_dict.get('invoice_id',False)
        if invoice_id:
            invoice_obj = self.browse(int(invoice_id))
            sale_order_obj = self.env["sale.order"].search([('name','=',invoice_obj.invoice_origin)],limit=1)

            transaction_id = sale_order_obj.transaction_ids.filtered(lambda transaction: transaction.state == 'done' or transaction.state == 'pending')
            transaction_id = transaction_id[0] if transaction_id else False
            if transaction_id and transaction_id.acquirer_id and transaction_id.acquirer_id.provider == 'cash_on_delivery':
                sellers_dict.update({
                    'payment_mode': 'cod_payment',
                    'payment_type': 'dr',
                })
                vals = {
                    "invoice_id": sellers_dict["invoice_id"],
                    "payment_type": sellers_dict["payment_type"],
                    "payment_mode": sellers_dict["payment_mode"],
                    "description": sellers_dict["description"],
                    "memo": sellers_dict["memo"],
                    "state": "confirm"
                }
                invoice_currency = sellers_dict["invoice_currency"]
                for seller in sellers_dict["seller_ids"].keys():
                    payment_method_ids = self.env[
                        "res.partner"].browse(seller).payment_method.ids
                    if payment_method_ids:
                        payment_method = payment_method_ids[0]
                    else:
                        payment_method = False
                    vals.update({"seller_id": seller})
                    vals.update({"payment_method": payment_method})
                    total_amount = 0

                    for amount in sellers_dict["seller_ids"][seller]["invoice_line_payment"]:
                        total_amount += amount
                    mp_currency_obj = self.env["res.currency"].browse(self.env['ir.default'].get('res.config.settings', 'mp_currency_id')) or self.env.user.currency_id

                    for invoice_line_id in sellers_dict["seller_ids"][seller]["invoice_line_ids"]:
                        invoice_line_obj = self.env["account.move.line"].browse(int(invoice_line_id))
                        total_amount += abs(invoice_line_obj.seller_commission)
                    vals['name'] = self.env['ir.sequence'].next_by_code(
                        'seller.payment') or 'NEW PAY'
                    vals.update({
                        "invoiced_amount": total_amount,
                        "payable_amount": invoice_currency.compute(total_amount, mp_currency_obj),
                        "invoice_line_ids": [(6, 0,sellers_dict["seller_ids"][seller]["invoice_line_ids"])],
                    })
                    seller_payment_id = self.env['seller.payment'].create(vals)
                    seller_payment_id.do_Confirm()
                    seller_payment_id.invoice_id.action_post()
        return result

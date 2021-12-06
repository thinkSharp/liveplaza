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
from odoo.exceptions import Warning


class SellerPaymentWizard(models.TransientModel):
    _inherit = 'seller.payment.wizard'

    def is_recieve_request_pending(self):
        seller_payment_obj = self.env["seller.payment"].search([("seller_id", "=", self.seller_id.id), (
            "state", "in", ["requested", "confirm"]), ("payment_mode", "=", "received_from_seller")], limit=1)
        if seller_payment_obj:
            return True
        return False

    def get_new_seller_payment(self):
        self.ensure_one()
        if self.cashable_amount >= 0:
            if self._context.get("by_seller", False):
                raise Warning(_("You can't pay now, due to insufficient amount."))
            else:
                raise Warning(_("You can't recieve from this seller, due to insufficient amount."))
        if self.amount > abs(self.cashable_amount):
            if self._context.get("by_seller", False):
                raise Warning(_("You can't pay more than the due amount."))
            else:
                raise Warning(_("You can't recieve more than the due amount."))
        if round(self.amount, 2) <= 0:
            if self._context.get("by_seller", False):
                raise Warning(_("Paying amount should be greater than 0. "))
            else:
                raise Warning(_("Recieving amount should be greater than 0. "))
        if self.is_recieve_request_pending():
            if self._context.get("by_seller", False):
                raise Warning(_("Your one request of payment is not done yet, so please wait..."))
            else:
                raise Warning(_("One request of payment is not done yet for this seller, so please wait..."))

        vals = {
            "date" : self.date,
            "seller_id": self.seller_id.id,
            "payment_method": self.payment_method_id.id or self.seller_id.payment_method.ids[0] if self.seller_id.payment_method else False,
            "payment_mode": "received_from_seller",
            "description": self.description or  _("Seller requested for payment..."),
            "payment_type": "cr",
            "state": "requested",
            "memo" : self.memo,
            "payable_amount": self.amount,
        }
        vals['name'] = self.env['ir.sequence'].next_by_code(
            'seller.payment') or 'NEW PAY'
        return self.env["seller.payment"].sudo().create(vals)



    def do_recieve(self):
        self.ensure_one()
        payment_id = self.get_new_seller_payment()
        seller_payment_menu_id = self.env[
            'ir.model.data'].get_object_reference('odoo_marketplace', 'wk_seller_payment_method')[1]
        seller_payment_action_id = self.env[
            'ir.model.data'].get_object_reference('odoo_marketplace', 'wk_seller_payment_action')[1]
        return {
            'type' : 'ir.actions.act_url',
            'url': '/web#id=%s&view_type=form&model=seller.payment&menu_id=%s&action=%s' % (payment_id.id, seller_payment_menu_id, seller_payment_action_id),
            'target': 'self',
        }


    def do_recieve_and_confirm(self):
        self.ensure_one()
        payment_id = self.get_new_seller_payment()
        payment_id.do_Confirm()
        seller_payment_menu_id = self.env[
            'ir.model.data'].get_object_reference('odoo_marketplace', 'wk_seller_payment_method')[1]
        seller_payment_action_id = self.env[
            'ir.model.data'].get_object_reference('odoo_marketplace', 'wk_seller_payment_action')[1]
        return {
            'type' : 'ir.actions.act_url',
            'url': '/web#id=%s&view_type=form&model=seller.payment&menu_id=%s&action=%s' % (payment_id.id, seller_payment_menu_id, seller_payment_action_id),
            'target': 'self',
        }

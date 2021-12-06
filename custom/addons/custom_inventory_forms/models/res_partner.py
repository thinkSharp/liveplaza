# -*- coding: utf-8 -*-

from odoo import api, models, fields, _


class ResPartner(models.Model):
    _inherit = 'res.partner'

    def create_request(self):
        res = []
        request_obj = self.env["product.request"]
        order_vals = {
            'seller_id': self.id,
        }

        request = request_obj.create(order_vals)
        res.append(request.id)

        return {
            "domain": [("id", "in", res)],
            "name": _("New"),
            "view_mode": "form",
            "res_model": "product.request",
            "view_id": False,
            "context": False,
            "type": "ir.actions.act_window",
        }


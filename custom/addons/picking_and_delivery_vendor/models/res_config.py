# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    vendor_max_seq = fields.Integer(string='Vendor Max Sequence')

    def get_values(self):
        res = super(ResConfigSettings, self).get_values()
        params = self.env['ir.config_parameter'].sudo()
        res.update(
            vendor_max_seq = int(params.get_param(
                'picking_and_delivery_vendor.vendor_max_seq'))
        )
        return res

    def set_values(self):
        super(ResConfigSettings, self).set_values()
        param = self.env['ir.config_parameter'].sudo()

        vendor_max_seq = self.vendor_max_seq or False

        param.set_param('picking_and_delivery_vendor.vendor_max_seq',
                        vendor_max_seq)
        
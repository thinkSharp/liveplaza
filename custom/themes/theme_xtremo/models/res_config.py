# -*- coding: utf-8 -*-
#################################################################################
#
#   Copyright (c) 2018-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>)
#   See LICENSE URL <https://store.webkul.com/license.html/> for full copyright and licensing details.
#################################################################################
from odoo import api, fields, models
import logging

_log = logging.getLogger(__name__)



class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'
    _name = "xtremo.res.config.settings"
    website_min_price_filter = fields.Integer(string='Website Product Minimum Price')
    website_max_price_filter = fields.Integer(string='Website Product Maximum Price')


    def set_values(self):
        super(ResConfigSettings, self).set_values()
        config = self.env['ir.default'].sudo()
        config.set('xtremo.res.config.settings', 'website_min_price_filter', self.website_min_price_filter)
        config.set('xtremo.res.config.settings', 'website_max_price_filter', self.website_max_price_filter)

    @api.model
    def get_values(self):
        res = super(ResConfigSettings, self).get_values()
        ICPSudo = self.env['ir.default'].sudo()
        min_price = ICPSudo.get('xtremo.res.config.settings', 'website_min_price_filter') or 0
        max_price = ICPSudo.get('xtremo.res.config.settings', 'website_max_price_filter') or 100000
        res.update(
            website_min_price_filter = min_price,
            website_max_price_filter = max_price
        )
        return res

# -*- coding: utf-8 -*-

from odoo import fields, models, api, _


class ResCountryTownship(models.Model):
    _inherit = 'res.country.township'

    rel_pickup_method_ids = fields.Many2many(
        'picking.method', 'pkup_tshp_rel', string='Pickup Zones')
    rel_delivery_method_ids = fields.Many2many(
        'delivery.method', 'deli_tshp_rel', string='Delivery Zones')

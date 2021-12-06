# -*- coding: utf-8 -*-

from odoo import fields, models, api, _


class DeliveryMethod(models.Model):
    _name = 'delivery.method'
    _description = 'Delivery Zone'

    name = fields.Char(string='Name', store=True, required=True,
                       copy=False, index=True)
    deli_price = fields.Float(
        string='Price', store=True, copy=False, index=False)
    active = fields.Boolean('Active', default=True)
    related_partner_ids = fields.Many2many(
        'res.partner', 'partner_deli_rel', string='Vendor', required=True)
    township_ids = fields.Many2many(
        'res.country.township', 'deli_tshp_rel', string='Allowed Townships')

# -*- coding: utf-8 -*- --

from odoo import api, models, fields, _


class ResCountryState(models.Model):
    _inherit = 'res.country.state'

    township_ids = fields.One2many(
        'res.country.township', 'country_id', 'Townships')
    
    active = fields.Boolean('Active', default=True)

    
    
class ResCountryTownship(models.Model):
    _name = 'res.country.township'
    _description = 'Township'

    name = fields.Char('Name', store=True, copy=False,
                       index=True, required=True)
    code = fields.Char('Code', store=True, copy=False)
    state_id = fields.Many2one(
        'res.country.state', 'State', ondelete='cascade', required=True)
    delivery_price = fields.Float('Delivery Price', store=True)
    country_id = fields.Many2one(
        'res.country', 'Country', ondelete='cascade', related='state_id.country_id')
    delivery_carrier_ids = fields.Many2many(
        'delivery.carrier', 'township_shipping_rel', string='Shipping Methods')
    active = fields.Boolean('Active', default=True)

    cod_availability = fields.Boolean('Cash on Delivery', default=True)

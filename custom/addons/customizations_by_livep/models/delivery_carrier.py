# -*- coding: utf-8 -*- --

from odoo import api, models, fields, _


class DeliveryCarrier(models.Model):
    _inherit = 'delivery.carrier'

    township_ids = fields.Many2many(
        'res.country.township', 'township_shipping_rel', string='Townships')

    shipping_method = fields.Selection([
        ('standard', "Standard"),
        ('Express', "Express")
    ], string='Shipping Method', required=True)
    vendor_id = fields.Many2one('res.partner', required=True, domain="[('company_type', '=', 'company'), ('is_default', '=', True)]", string='Vendor')

    def _match_address(self, partner):
        self.ensure_one()
        if self.country_ids and partner.country_id not in self.country_ids:
            return False
        if self.state_ids and partner.state_id not in self.state_ids:
            return False
        if self.township_ids and partner.township_id not in self.township_ids:
            return False
        if self.zip_from and (partner.zip or '').upper() < self.zip_from.upper():
            return False
        if self.zip_to and (partner.zip or '').upper() > self.zip_to.upper():
            return False
        return True

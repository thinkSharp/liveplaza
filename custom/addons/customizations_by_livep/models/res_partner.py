# -*- coding: utf-8 -*-

from odoo import api, models, fields, _


class ResPartner(models.Model):
    _name = 'res.partner'
    _inherit = 'res.partner'

    township_id = fields.Many2one(
        'res.country.township', 'Township', ondelete='cascade')
    seller_subscription_id = fields.Many2one(
        'subscription.plan', string='Subscription', ondelete='cascade')
    sales_type = fields.Selection(
        [('products', 'Products'), ('services', 'Services'), ('products_services', 'Products and Services')], 'Sales Type', default='products', store=True)

    def _default_user_group(self):
        return self.env['res.groups'].search([('name', '=', 'Seller Tier 1 (arc)')], limit=1).id

    group_id = fields.Many2one(
        'res.groups', 'Users Group', read=['odoo_marketplace.marketplace_seller_group'], ondelete='cascade',
        domain=[("name", "in", ("Seller Tier 1 (arc)", "Seller Tier 2 (arc)", "Seller Tier 3 (arc)"))],
        default=_default_user_group)

    def approve(self):
        self.ensure_one()
        if self.seller:
            user = self.env['res.users'].search(
                [('partner_id.id', '=', self.id)])
            user.write({'groups_id': [(4, self.env.ref('base.group_user').id),
                                        (3, self.env.ref('base.group_portal').id)]})
            self.state = "approved"

    @api.onchange('township_id')
    def get_state(self):
        for record in self:
            record.state_id = record.township_id.state_id

    def _display_address(self, without_company=False):
        address_format = self._get_address_format()
        args = {
            'state_code': self.state_id.code or '',
            'state_name': self.state_id.name or '',
            'country_code': self.country_id.code or '',
            'country_name': self._get_country_name(),
            'company_name': self.commercial_company_name or '',
            # Township
            'township_name': self.township_id.name or '',

        }
        for field in self._formatting_address_fields():
            args[field] = getattr(self, field) or ''
        if without_company:
            args['company_name'] = ''
        elif self.commercial_company_name:
            address_format = '%(company_name)s\n' + address_format
        return address_format % args

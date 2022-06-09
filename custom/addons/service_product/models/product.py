from odoo import fields, models, api, _, exceptions


class ProductInherit(models.Model):
    _inherit = 'product.template'

    is_service = fields.Boolean(string="Service Type", default=False)

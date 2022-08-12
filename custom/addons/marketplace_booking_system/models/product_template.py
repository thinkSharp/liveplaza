from odoo import api, fields, models, _

class ProductTemplate(models.Model):
    _inherit = 'product.template'


    @api.model
    def create(self, vals):
        vals['type'] = 'service'
        vals['invoice_policy'] = 'order'
        return super(ProductTemplate, self).create(vals)


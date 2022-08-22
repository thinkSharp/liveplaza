from odoo import api, fields, models, _

class ProductTemplate(models.Model):
    _inherit = 'product.template'
    image_1920 = fields.Image("Image", required=True)
    @api.model
    def create(self, vals):
        vals['invoice_policy'] = 'order'
        return super(ProductTemplate, self).create(vals)
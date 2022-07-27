
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError

class FeelingProducts(models.Model):
    _name = "feeling.products"
    _description = "Categorize the products on feelings"
    _order = "sequence"

    name = fields.Char(string="Name", required=True)
    feeling_emoji = fields.Image(string="Emoji", required=True)
    feeling_text = fields.Char(string="Description")
    feeling_noun = fields.Char(string="Noun", required=True)
    feeling_product_categories = fields.Many2many('product.public.category', String="Product Categories", required=True)
    website_published = fields.Boolean('Published', copy=False, default=False)
    sequence = fields.Integer(string='Sequence', default=30)

    def toggle_website_published(self):
        """ Inverse the value of the field ``website_published`` on the records in ``self``. """
        for record in self:
            record.website_published = not record.website_published

    @api.constrains('sequence')
    def _check_value(self):
        if self.sequence <= 0:
            raise ValidationError(_('Enter the sequence value greater than 0'))

    @api.constrains('name')
    def _check_name(self):
        if self.name.isdigit():
            raise ValidationError(_('The feeling name should be alphanumeric'))


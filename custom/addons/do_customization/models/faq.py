
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class FAQ(models.Model):
    _name = "website.faq"
    _description = "Frequently asked question"
    _order = "sequence"

    question = fields.Html(string="Question", required=True)
    answer = fields.Html(string="Answer", required=True)
    question_myanmar = fields.Html(string="Myanmar Language Question", required=True)
    answer_myanmar = fields.Html(string="Myanmar Language Answer", required=True)
    sequence = fields.Integer(string="Sequence")
    website_published = fields.Boolean(stirng="Published", copy=False, default=True)
    parent_id = fields.Many2one('faq.category', string='Parent Category', required=True)

    def toggle_website_published(self):
        """ Inverse the value of the field ``website_published`` on the records in ``self``. """
        for record in self:
            record.website_published = not record.website_published

    @api.constrains('sequence')
    def _check_value(self):
        if self.sequence <= 0:
            raise ValidationError(_('Enter the sequence value greater than 0'))


class FAQCategory(models.Model):
    _name = 'faq.category'
    _description = "FAQ Category"
    _order = 'sequence'

    name = fields.Char("FAQ Category", required=True)
    sequence = fields.Integer(string="Sequence")
    website_published = fields.Boolean(stirng="Published", copy=False, default=True)

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
            raise ValidationError(_('The name should be alphanumeric'))


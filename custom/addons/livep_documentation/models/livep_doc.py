from odoo import api, fields, models


class LivepDocumentation(models.Model):
    _name = 'livep.documentation'
    _description = 'Liveplaza Documentation'

    name = fields.Char("Document Category", required=True)

class CreateDocument(models.Model):
    _name = 'create.documents'
    _description = 'Creat Document'

    category = fields.Many2one('livep.documentation', string="Document Category", required=True)
    title = fields.Html(string="Document Title", required=True)
    contents = fields.Html(string="Contents", required=True)

    

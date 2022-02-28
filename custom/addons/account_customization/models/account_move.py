from odoo import models, fields, api, _


class AccountMove(models.Model):
    _inherit = 'account.move'
    
    
    name = fields.Char(string='Reference', required=True, readonly=True, copy=False, default='/')
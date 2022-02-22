from odoo import fields, models, api, _, exceptions
import datetime


class LivepResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'
    domain = fields.Selection(
        [('localhost', 'Localhost'), ('online', 'Online'), ('dev', 'Dev'),
         ], string='domain')
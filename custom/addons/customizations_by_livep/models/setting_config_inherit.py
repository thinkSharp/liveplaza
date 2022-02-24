from odoo import fields, models, api, _, exceptions
import datetime


class LivepResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'
    domain = fields.Char( string='domain', config_parameter='customizations_by_livep.domain')
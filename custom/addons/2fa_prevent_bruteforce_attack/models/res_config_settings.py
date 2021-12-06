# -*- coding: utf-8 -*-

from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    is_open_2fa = fields.Boolean(related='company_id.is_open_2fa', string="Open 2FA", readonly=False)

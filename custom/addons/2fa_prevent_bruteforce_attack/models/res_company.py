# -*- coding: utf-8 -*-

from odoo import models, fields


class ResCompany(models.Model):
    _inherit = "res.company"

    is_open_2fa = fields.Boolean(string="Open 2FA", default=False)

# -*- coding: utf-8 -*-
##############################################################################
# Copyright (c) 2015-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>)
# See LICENSE file for full copyright and licensing details.
# License URL : <https://store.webkul.com/license.html/>
##############################################################################


from odoo import models, fields, api, _


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    def _check_smspoh(self):
        result = self.env['ir.module.module'].search(
            [('name', '=', 'smspoh_gateway')])
        if result:
            return True
        else:
            return False

    module_smspoh_gateway = fields.Boolean(
        string='Install smspoh SMS Gateway',
        help='It will Install smspoh sms gateway automatically.',
        default=False)
    is_smspoh_in_addon = fields.Boolean(default=_check_smspoh)

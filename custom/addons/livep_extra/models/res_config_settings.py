# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    approved_by_admin_cod = fields.Boolean(string='Approved by Admin for COD', config_parameter='sale.approved_by_admin_cod')
    approved_by_admin_prepaid = fields.Boolean(string='Approved by Admin for Prepaid', config_parameter='sale.approved_by_admin_prepaid')
    #if self.env['ir.config_parameter'].sudo().get_param('sale.use_quotation_validity_days'):


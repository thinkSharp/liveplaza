from odoo import fields, models, api, _, exceptions
import datetime


class MultiResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'
    warehouse_location = fields.Many2one('stock.location', string='Location for Multi Product', config_parameter='multi_product_request.warehouse_location')
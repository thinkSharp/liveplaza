# -*- coding: utf-8 -*-

from odoo import tools
from odoo import api, fields, models


class PickupReport(models.Model):
    _name = 'pickup.report'
    _description = 'Pickup Report'
    _auto = False
    _order = 'scheduled_date desc'

    scheduled_date = fields.Datetime(string='Scheduled Date')
    origin = fields.Char(string='Source')
    state = fields.Selection(
        [('draft', 'Draft'), ('pick', 'Picked'), ('cancel', 'Cancelled')], string='State')
    picking_address = fields.Char(string='Pickup Address')
    product_id = fields.Many2one('product.product', string='Item', ondelete='cascade')
    seller_id = fields.Many2one('res.partner', string='Seller', ondelete='cascade')
    vendor_id = fields.Many2one('res.partner', string='Vendor', ondelete='cascade')

    def init(self):
        tools.drop_view_if_exists(self._cr, 'pickup_report')
        self._cr.execute("""
            CREATE OR REPLACE VIEW pickup_report AS (
                SELECT pm.id as id,
                pm.scheduled_date as scheduled_date,
                sol.product_id as product_id,
                pm.origin as origin,
                pm.vendor_id as vendor_id,
                sol.marketplace_seller_id as seller_id,
                CONCAT(rp.street, ', ', rp.street2, ', ', tsp.name, ', ', st.name) as picking_address,
                pm.state as state
                FROM picking_move pm
                LEFT JOIN sale_order_line sol on pm.mp_order_id = sol.id
                LEFT JOIN res_partner rp on pm.picking_address = rp.id
                LEFT JOIN res_country_township tsp on rp.township_id = tsp.id
                LEFT JOIN res_country_state st on rp.state_id = st.id)""")

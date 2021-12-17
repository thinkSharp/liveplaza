# -*- coding: utf-8 -*-

from odoo import tools
from odoo import api, fields, models


class DeliveryReport(models.Model):
    _name = 'delivery.report'
    _description = 'Delivery Report'
    _auto = False
    _order = 'scheduled_date desc'

    scheduled_date = fields.Datetime(string='Scheduled Date')
    origin = fields.Char(string='Source')
    state = fields.Selection(
        [('draft', 'Draft'),
         ('wating', 'Waiting Another Operation'),
         ('confirmed', 'Waiting'),
         ('assigned', 'Ready'),
         ('done', 'Done'),
         ('cancel', 'Cancelled')], string='State')
    delivery_address = fields.Char(string='Delivery Address')
    buyer_id = fields.Many2one('res.partner', string='Buyer', ondelete='cascade')
    vendor_id = fields.Many2one('res.partner', string='Vendor', ondelete='cascade')
    product_id = fields.Many2one('product.product', string='Item', ondelete='cascade')

    def init(self):
        tools.drop_view_if_exists(self._cr, 'delivery_report')
        self._cr.execute("""
            CREATE OR REPLACE VIEW delivery_report AS (
                SELECT sp.id as id,
                sol.product_id as product_id,
                sp.scheduled_date as scheduled_date,
                sp.origin as origin,
                sp.vendor_id as vendor_id,
                sp.partner_id as buyer_id,
                CONCAT(rp.street, ', ', rp.street2, ', ', tsp.name, ', ', st.name) as delivery_address,
                sp.state as state
                FROM stock_picking sp
                LEFT JOIN sale_order so on sp.origin = so.name
                LEFT JOIN sale_order_line sol on sol.order_id = so.id
                LEFT JOIN res_partner rp on sp.partner_id = rp.id
                LEFT JOIN res_country_township tsp on rp.township_id = tsp.id
                LEFT JOIN res_country_state st on rp.state_id = st.id)""")

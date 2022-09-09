# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from collections import defaultdict
from datetime import datetime
from dateutil import relativedelta
from itertools import groupby
from operator import itemgetter
from re import findall as regex_findall, split as regex_split

from odoo import api, fields, models, _, SUPERUSER_ID
from odoo.exceptions import UserError
from odoo.osv import expression
from odoo.tools.float_utils import float_compare, float_round, float_is_zero


class StockMove(models.Model):
    _inherit = "stock.move"


    order_line_id = fields.Many2one("sale.order.line", string="Sale Order Line")
 

    @api.model_create_multi
    def create(self, vals_list):
        # TDE CLEANME: why doing this tracking on picking here ? seems weird
        tracking = []
        for vals in vals_list:
            
            #####################################################
            if vals.get('sale_line_id'):
                vals['order_line_id'] = vals.get('sale_line_id')
            else:
                if vals.get('origin'):
                    sol_obj = self.env["sale.order.line"].sudo().search([('order_id.name', '=', vals.get('origin')), ('product_id', '=', vals.get('product_id'))], limit=1)
                    if sol_obj:
                        vals['order_line_id'] = sol_obj.id
            #####################################################
            
            if not self.env.context.get('mail_notrack') and vals.get('picking_id'):
                picking = self.env['stock.picking'].browse(vals['picking_id'])
                initial_values = {picking.id: {'state': picking.state}}
                tracking.append((picking, initial_values))
        res = super(StockMove, self).create(vals_list)
        for picking, initial_values in tracking:
            picking.message_track(picking.fields_get(['state']), initial_values)
        return res


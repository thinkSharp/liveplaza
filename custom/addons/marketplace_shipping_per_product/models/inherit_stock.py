# -*- coding: utf-8 -*-
#################################################################################
# Author      : Webkul Software Pvt. Ltd. (<https://webkul.com/>)
# Copyright(c): 2015-Present Webkul Software Pvt. Ltd.
# License URL : https://store.webkul.com/license.html/
# All Rights Reserved.
#
#
#
# This program is copyright property of the author mentioned above.
# You can`t redistribute it and/or modify it.
#
#
# You should have received a copy of the License along with this program.
# If not, see <https://store.webkul.com/license.html/>
#################################################################################
from odoo import models, fields, api, _

import logging
_logger = logging.getLogger(__name__)

class StockMove(models.Model):
    _inherit = 'stock.move'

    def sol_assign_picking(self):
        Picking = self.env['stock.picking']
        for move in self:
            sol_grouping = move.sale_line_id.order_id.carrier_id.sol_grouping
            sol_grouping = True if sol_grouping == 'y' else False
            new_picking = False
            domain = [
                ('carrier_id', '=', move.sale_line_id.delivery_carrier_id.id),
                ('group_id', '=', move.group_id.id),
                ('location_id', '=', move.location_id.id),
                ('location_dest_id', '=', move.location_dest_id.id),
                ('picking_type_id', '=', move.picking_type_id.id),
                ('marketplace_seller_id', '=',move.product_id.marketplace_seller_id.id),
                ('printed', '=', False),
                ('state', 'in', ['draft', 'confirmed', 'waiting', 'partially_available', 'assigned']),
            ]
            if not sol_grouping:
                domain += [('unique_grp_key', '=', move.sale_line_id.unique_grp_key)]
            picking = Picking.search(domain, limit=1)
            if not picking:
                new_picking = True
                values = move._get_new_picking_values()
                values.update({
                    'carrier_id' : move.sale_line_id.delivery_carrier_id.id,
                    'unique_grp_key' : move.sale_line_id.unique_grp_key
                })
                picking = Picking.create(values)
            move.write({'picking_id': picking.id})
        return True

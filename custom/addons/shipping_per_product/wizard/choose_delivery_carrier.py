# -*- coding: utf-8 -*-
##########################################################################
# 2010-2017 Webkul.
#
# NOTICE OF LICENSE
#
# All right is reserved,
# Please go through this link for complete license : https://store.webkul.com/license.html
#
# DISCLAIMER
#
# Do not edit or add to this file if you wish to upgrade this module to newer
# versions in the future. If you wish to customize this module for your
# needs please refer to https://store.webkul.com/customisation-guidelines/ for more information.
#
# @Author        : Webkul Software Pvt. Ltd. (<support@webkul.com>)
# @Copyright (c) : 2010-2017 Present Webkul Software Pvt. Ltd. (<https://webkul.com/>)
# @License       : https://store.webkul.com/license.html
#
##########################################################################
from odoo import fields, models, api, _
from odoo.exceptions import UserError

import logging
_logger = logging.getLogger(__name__)

class ChooseDeliveryCarrier(models.TransientModel):
    _inherit = 'choose.delivery.carrier'

    @api.model
    def default_get(self,default_fields):
        res = super(ChooseDeliveryCarrier,self).default_get(default_fields)
        order_id = self.env['sale.order'].browse(self._context.get('active_id'))
        line_ids = order_id.order_line.filtered(lambda l: l.product_id.type != 'service' and l.is_delivery == False)
        res['line_ids'] = line_ids.ids
        return res

    line_ids = fields.Many2many("sale.order.line")
    is_sol_carrier = fields.Boolean("SOL Carrier", related="carrier_id.is_sol_carrier")

    @api.onchange('carrier_id')
    def _onchange_carrier_id(self):
        if self.is_sol_carrier:
            self.delivery_message = False
            self.display_price = 0
            self.delivery_price = 0
        else:
            return super(ChooseDeliveryCarrier, self)._onchange_carrier_id()

    def _get_shipment_rate(self):
        if self.is_sol_carrier:
            vals = self.carrier_id.sol_carrier_rate_shipment(self.order_id)
            if vals.get('success'):
                self.delivery_message = vals.get('warning_message', False)
                self.delivery_price = vals['price']
                self.display_price = vals['carrier_price']
                return {}
            return {'error_message': vals['error_message']}
        else:
            return super(ChooseDeliveryCarrier, self)._get_shipment_rate()

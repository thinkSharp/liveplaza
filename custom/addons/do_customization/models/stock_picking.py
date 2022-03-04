# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from ast import literal_eval
from datetime import date
from itertools import groupby
from operator import itemgetter
import time

from odoo import api, fields, models, SUPERUSER_ID, _
from odoo.osv import expression
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
from odoo.tools.float_utils import float_compare, float_is_zero, float_round
from odoo.exceptions import UserError
from odoo.addons.stock.models.stock_move import PROCUREMENT_PRIORITIES


class Picking(models.Model):
    _inherit = "stock.picking"

    # payment_provider = fields.Selection(selection=[('manual', 'Custom Payment Form'),('transfer', 'Manual Payment'),
    #                                                ('cash_on_delivery', 'COD')], string='Provider')
    #
    # is_admin_approved = fields.Boolean('Admin Approved', default=False) 
    
    #is_seller_approved = fields.Boolean('Seller Approved', default=False)
# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class ResUsers(models.Model):
    _inherit = 'res.users'

    seller_subscription = fields.Selection(
        [('basic', 'Basic'), ('basic_plus', 'Basic PLUS'), ('pro', 'Pro')], 'Subscription', default='basic', store=True)
    sales_type = fields.Selection(
        [('products', 'Products'), ('services', 'Services'), ('products_services', 'Products and Services')], 'Sales Type', default='products', store=True)

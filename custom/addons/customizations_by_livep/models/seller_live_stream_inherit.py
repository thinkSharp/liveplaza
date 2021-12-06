# -*- coding: utf-8 -*-
from odoo import models, fields, api, _


class SellerLiveStream(models.Model):
    _inherit = 'seller.live.stream'

    host = fields.Selection(
        [('youtube', 'YouTube'), ('facebook', 'Facebook')], string='Host', store=True, default='youtube')

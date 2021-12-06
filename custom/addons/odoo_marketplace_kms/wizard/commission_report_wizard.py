# -*- coding: utf-8 -*-

from odoo import models, fields, api
from datetime import datetime
import csv

from odoo.tools import DEFAULT_SERVER_DATE_FORMAT as DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT as DATETIME_FORMAT


class CommissionReportWizard(models.TransientModel):
    _name = 'commission.report.wizard'
    _description = 'Commission Report Wizard'

    date_start = fields.Date(
        string='From', required=True, default=fields.Date.today)
    date_end = fields.Date(string='To', required=True,
                           default=fields.Date.today)
    marketplace_seller_id = fields.Many2one(
        'res.partner', string='Seller', required=True, ondelete='cascade')

   
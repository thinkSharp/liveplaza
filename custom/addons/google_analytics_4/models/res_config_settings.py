# -*- coding: utf-8 -*-

from odoo import models, fields


class GoogleAnalytics4ConfigSettings(models.TransientModel):
  _inherit = 'res.config.settings'

  has_google_analytics_4 = fields.Boolean("Google Analytics 4", related="website_id.has_google_analytics_4", readonly=False)
  measurement_id = fields.Char("Measurement ID", related="website_id.measurement_id", readonly=False)

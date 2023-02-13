# -*- coding: utf-8 -*-

from odoo import models, fields


class GoogleAnalytics4Website(models.Model):
  _inherit = 'website'

  def _inverse_has_google_analytics_4(self):
    if not self.has_google_analytics_4:
      self.measurement_id = ''

  has_google_analytics_4 = fields.Boolean("Google Analytics 4", inverse=_inverse_has_google_analytics_4)
  measurement_id = fields.Char("Measurement ID")

from odoo import models, api


class ResPartner(models.Model):
  _inherit = 'res.partner'

  @api.model
  def signup_retrieve_info(self, token):
    res = super(ResPartner, self).signup_retrieve_info(token)
    partner = self._signup_retrieve_partner(token, raise_exception=True)
    if partner:
      res['phone'] = partner.phone or ''
    return res

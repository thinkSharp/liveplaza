# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models, api, _

class Website(models.Model):
    _inherit = 'website'

    def get_country_list(self):            
        country_ids=self.env['res.country'].search([])
        return country_ids
        
    def get_state_list(self):            
        state_ids=self.env['res.country.state'].search([])
        return state_ids

    def get_township_list(self):
        township_ids=self.env['res.country.township'].search([])
        return township_ids

    def get_township_list_by_state(self, state):
        township_ids=self.env['res.country.township'].search([('state_id', '=', state)])
        return township_ids
        
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:


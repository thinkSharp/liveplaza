# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'
    
    journal_id = fields.Many2one('account.journal', string='Journal', ondelete='cascade')
    
    @api.model
    def get_values(self):
        res = super(ResConfigSettings, self).get_values()
        params = self.env['ir.config_parameter'].sudo()
        res.update(            
            journal_id=int(params.get_param(
                'picking_and_delivery_vendor.journal_id')),
        )
        return res


    def set_values(self):
        super(ResConfigSettings, self).set_values()
        param = self.env['ir.config_parameter'].sudo()        
        journal_id = self.journal_id and self.journal_id.id or False
        param.set_param('picking_and_delivery_vendor.journal_id',
                        journal_id)
        

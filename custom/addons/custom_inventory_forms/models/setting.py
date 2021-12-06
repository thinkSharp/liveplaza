# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'
    
    location_id = fields.Many2one('stock.location', string='Location', ondelete='cascade')
    pricelist_id = fields.Many2one('product.pricelist', string='Price List', ondelete='cascade')
    
    @api.model
    def get_values(self):
        res = super(ResConfigSettings, self).get_values()
        params = self.env['ir.config_parameter'].sudo()
        res.update(            
            location_id=int(params.get_param('custom_inventory_forms.location_id')),
            pricelist_id=int(params.get_param('custom_inventory_forms.pricelist_id')),
        )
        return res
    
    


    def set_values(self):
        super(ResConfigSettings, self).set_values()
        param = self.env['ir.config_parameter'].sudo()        
        location_id = self.location_id and self.location_id.id or False
        pricelist_id = self.pricelist_id and self.pricelist_id.id or False
        param.set_param('custom_inventory_forms.location_id', location_id)
        param.set_param('custom_inventory_forms.pricelist_id', pricelist_id)
        
        
        
        
        
        
        
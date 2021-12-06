from odoo import api, models, fields, _
from datetime import datetime
from odoo.exceptions import UserError

class ProductVariantsRequestWiz(models.Model):
    _name = 'product.variants.request.wiz'
    
        
#     @api.model
#     def _default_product(self):
#          
#         product_list = [] 
#         product_tmpl_obj =self.env['product.product'].search[('product_tmpl_id.marketplace_seller_id', '=', self.env.user.partner_id.id), ('status', '=', 'approved')]
#         if product_tmpl_obj:
#             for product in product_tmpl_obj:
#                 product_list.append(product.id)
#             return [('id', 'in', tuple(product_list))]
#         else:
#             return []

    product_id = fields.Many2one('product.template', string='Product')
    
    def create_product_template(self):  
        product_variant = self.env['product.variants.request'].browse(self._context.get('active_ids', []))      
        product_variant_line = self.env['product.variants.request.line'].browse(self._context.get('active_ids', []))
        product_obj =self.env['product.product'].search([('product_tmpl_id', '=', self.product_id.id)])          
        for pobj in product_obj:
            quant_obj =self.env['stock.quant'].search([('product_id', '=', pobj.id),('quantity','>', 0 )])
            old = 0
            for qobj in quant_obj:
                if qobj.quantity > 0:
                    old = qobj.quantity
            product_variant_line.sudo().create({          
                'product_id': pobj.id,
                'product_variants_request_id': product_variant.id,
                'old_qty' : old
                
            })

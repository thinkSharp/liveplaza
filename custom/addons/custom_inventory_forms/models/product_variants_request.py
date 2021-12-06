# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo import SUPERUSER_ID
from lxml import etree
from datetime import datetime, timedelta
import odoo.addons.decimal_precision as dp
from odoo.tools.translate import _
from odoo.exceptions import except_orm, Warning, RedirectWarning, UserError
# from .mp_tools import *
import logging
_logger = logging.getLogger(__name__)

class ProductVariantsRequest(models.Model):
    _name = 'product.variants.request'
    _description = 'Product Variants Request'
    _order = 'id desc'
    
    
    name = fields.Char(string='Name', copy=False,
                       store=True, index=True, default='New')
    request_date = fields.Date(
        string='Requested Date', store=True, default=datetime.today())
    seller_id = fields.Many2one('res.partner', string='Seller',
                                default=lambda self: self.env.user.partner_id.id, ondelete='cascade')
    state = fields.Selection([("draft", "Draft"), ("requested", "Requested"), (
        "approved", "Approved"), ("rejected", "Rejected")], string="Status", default="draft", copy=False)
    product_variants_request_line_ids = fields.One2many(
        'product.variants.request.line', 'product_variants_request_id', string='Product Varinats Request Lines' )
    
    product_id = fields.Many2one('product.product', string='Product')
    
    
    @api.model
    def create(self, vals):
        obj = super(ProductVariantsRequest, self).create(vals)
        if obj.name == 'New':
            sequence = self.env['ir.sequence'].get(
                'product.variants.request.seq') or 'New'
            obj.write({'name': sequence})
        return obj
    
    def reject(self):
        for obj in self:
            if obj.state == "requested":
                obj.write({"state": "rejected"})
                
    def set_2_draft(self):
        for obj in self:
            obj.write({"state": "draft"})
    
    def approve(self):
        self._approve()

    def _approve(self):
        if not self.user_has_groups('stock.group_stock_manager'):
            raise UserError(_("MP inventory request can not be approved. Only stock manager can approve inventory request."))
        for obj in self:
            if obj.state == "requested":
                obj.sudo().change_product_qty()
                obj.write({"state": "approved"})
            else:
                _logger.info("-------- MP inventory request can not be approved. Inventory request not in requested state or product is not approved or product seller is not approved. ----------")
    
    def request(self):
        for obj in self.product_variants_request_line_ids:
            if obj.onhand_qty < 0:
                raise Warning(_("Quantity cannot be negative."))
            if obj.onhand_qty == 0:
                raise Warning(_("Quantity must be different from zero."))
            if obj.lst_price < 0:
                raise Warning(_("Price cannot be negative."))
            if obj.lst_price == 0:
                raise Warning(_("Price must be different from zero."))
            self.state = "requested"
            self.auto_approve()

    def auto_approve(self):
        for obj in self.product_variants_request_line_ids:
            if obj.product_variants_request_id.seller_id.get_seller_global_fields('auto_approve_qty'):
                self.with_user(SUPERUSER_ID)._approve()
                
    def change_product_qty(self):
        location_id = int(self.env['ir.config_parameter'].sudo().get_param('custom_inventory_forms.location_id'))
        pricelist_id = int(self.env['ir.config_parameter'].sudo().get_param('custom_inventory_forms.pricelist_id'))
        for template_obj in self.product_variants_request_line_ids:            
            if template_obj.onhand_qty < 0:
                raise Warning(_('Initial Quantity can not be negative'))
#             and template_obj.product_id.marketplace_seller_id.state == "approved"
            if template_obj.product_id.status == "approved": 
                vals = {
                    'product_id': template_obj.product_id.id,
                    'inventory_quantity': template_obj.onhand_qty,
                    'location_id': location_id,
                   
                }
                self.env['stock.quant'].sudo().with_context(inventory_mode=True).create(vals)
                
            product_obj = self.env['product.product'].search([('id', '=', template_obj.product_id.id)])
            for product in product_obj:
                    self.env['product.pricelist.item'].create({                                                                                               
                        'pricelist_id':pricelist_id,
                        'product_id': product.id,                             
                        'fixed_price':template_obj.lst_price,
                        })
                    
                    product.update({
                        'image_1920': template_obj.image1,                                          
                        })
                    
#             product_tmpl = self.env['product.template'].search([('id', '=', product_obj.product_tmpl_id.id)])
#             product_tmpl.update({
#                         'lst_price': template_obj.lst_price,                                          
#                         })
                    

    
class ProductVariantsRequestLine(models.Model):
    _name = 'product.variants.request.line'
    _description = 'Product Variants Request Line'
    _rec_name = 'product_id'
    _order = 'id desc'
    
    

    
    product_variants_request_id = fields.Many2one('product.variants.request', string='Product Variants Request',  ondelete='cascade')
    product_id = fields.Many2one('product.product', string='Product')
#     product_tmpl_id = fields.Many2one('product.template', string='Product')
#     odoo_seller_id = fields.Many2one('res.partner', string='Seller')
    onhand_qty = fields.Integer('Quantity', size=3, required=True)
    old_qty = fields.Integer('Old Quantity')
    lst_price = fields.Float('Price', size=9, required=True)
    image1 = fields.Binary('Image 1')
    image2 = fields.Binary('Image 2')
    image3 = fields.Binary('Image 3')
    
    
    
    @api.constrains('lst_price')
    def lst_price_constratints(self):               
        price = str(self.lst_price)
        if len(price) > 9 :
            raise UserError('Invalid Price')
        
    @api.constrains('onhand_qty')
    def onhand_qty_constratints(self):              
        product_qty = str(self.onhand_qty)
        if len(product_qty) > 3 :
            raise UserError('Invalid Qty')
        
#     @api.onchange('image1')
#     def image1_onchange(self):
#         if self.onhand_qty == 0 :
#             raise UserError('Qty must be different from zero')
#         if self.lst_price == 0.00 :
#             raise UserError('Price must be different from zero')
    
    
    
    
    
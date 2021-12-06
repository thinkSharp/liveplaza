# -*- coding: utf-8 -*-

from odoo import api, models, fields, _
from datetime import datetime
from odoo.exceptions import UserError


class ProductRequest(models.Model):
    _name = 'product.request'
    _description = 'Product Request'
    _order = 'id desc'

    name = fields.Char(string='Name', copy=False,
                       store=True, index=True, default='New')
    request_date = fields.Date(
        string='Requested Date', store=True, default=datetime.today())
    seller_id = fields.Many2one('res.partner', string='Seller',
                                default=lambda self: self.env.user.partner_id.id, ondelete='cascade')
    state = fields.Selection([
        ('draft', 'Draft'),
        ('request', 'Requested'),
        ('done', 'Done'),
        ('cancel', 'Cancelled'),
    ], string='Status', readonly=True, copy=False, index=True, tracking=3, default='draft')
    product_request_line_ids = fields.One2many(
        'product.request.line', 'product_request_id', string='Product Request Lines')
    
    
    
    
    @api.model
    def create(self, vals):
        obj = super(ProductRequest, self).create(vals)
        if obj.name == 'New':
            sequence = self.env['ir.sequence'].get(
                'product.request.seq') or 'New'
            obj.write({'name': sequence})
        return obj

    def action_request(self):
        self.write({'state': 'request'})

    def action_done(self):
        for request in self.product_request_line_ids:
            name = request.product
            ref = request.product_id
            mp_seller_id = request.seller_id.id
#             categ_id = request.categ.id
            price = request.price
            image_1920 = request.image_1
#             sale_delay = request.customer_lead
            qty_available = request.product_qty
            note = request.note
            vals = {
                'name': name,
                'default_code' : ref,
                'sale_ok' : True,
                'type' : 'product',
                'property_account_income_id' : 442,
                'marketplace_seller_id': mp_seller_id,
#                 'categ_id' : categ_id,
                'list_price' : price,
                'image_1920' : image_1920,
#                 'sale_delay' : sale_delay,
                'status' : 'approved',
                'invoice_policy': 'order', 
                'qty_available': qty_available,             
                'public_categ_ids': [(6, 0, request.categ_ids.ids)],   
                'description' : note,
                'alternative_product_ids': [(6, 0, request.alternative_product_ids.ids)], 
                'product_template_image_ids': [(6, 0, request.product_template_image_ids.ids)],
                'wk_product_tab_ids': [(6, 0, request.wk_product_tab_ids.ids)]
            }
            product_tmpl_obj = self.env['product.template'].create(vals)
            product_obj = self.env['product.product'].search([('product_tmpl_id', '=', product_tmpl_obj.id)])
            quants = request.sudo().change_product_qty(product_obj)
                        
            for line in request: 
                for att_line in line.attribute_line_ids: 
                    lines ={
                        'attribute_id': att_line.attribute_id.id,
                        'product_tmpl_id': product_tmpl_obj.id,
                        'value_ids': [(6, 0, att_line.value_ids.ids)]
                        }          
                    self.env['product.template.attribute.line'].create(lines)    
#                 
        self.write({'state': 'done'})
        return product_tmpl_obj
            
    
    
    def action_cancel(self):
        self.write({'state': 'cancel'})


class ProductRequestLine(models.Model):
    _name = 'product.request.line'
    _description = 'Product Request Line'
    _rec_name = 'product_id'
    _order = 'id desc'
    
    
    def _get_default_alternative_products(self):          
        self.ensure_one() 
        if self.env.user:                            
            self.write({
                'alternative_products': self.env['product.template'].search([('marketplace_seller_id', '=', self.env.user.id)]),                        
            })
        

    product_request_id = fields.Many2one(
        'product.request', string='Product Request',  ondelete='cascade')
    product = fields.Char(string='Product', translate=True, store=True)
    product_id = fields.Char(string='Product ID', copy=False,
                       store=True, index=True, default='-')
    seller_id = fields.Many2one('res.partner', string='Seller',
                                default=lambda self: self.env.user.partner_id.id, ondelete='cascade')
#     categ = fields.Many2one('product.public.category', string='Category')
    categ_ids = fields.Many2many('product.public.category', string='Category')
    price = fields.Float(string='Price', size=9, required=True)
    color = fields.Char(string='Color', store=True)
    size = fields.Char(string='Size',  store=True)
    accessory_product = fields.Char(string='Accessories', translate=True, store=True)
    customer_lead = fields.Integer(
        string='Lead', store=True, help="Days for delivery")
    image_1 = fields.Binary('Image 1')
    image_2 = fields.Binary('Image 2')
    image_3 = fields.Binary('Image 3')
    image_4 = fields.Binary('Image 4')
    image_5 = fields.Binary('Image 5')
    attribute_line_ids = fields.One2many('product.request.attribute.line', 'product_request_line_id', 'Product Attributes', copy=False)
    product_qty = fields.Integer(string="Product Qty", size=3, required=True)
    note = fields.Text(string="Note")
    alternative_product_ids = fields.Many2many(
        'product.template', 'product_request_template_rel', 'src_id', 'dest_id', 
        string='Alternative Products', help='Suggest alternatives to your customer (upsell strategy). '
                                            'Those products show up on the product page.')
    product_template_image_ids = fields.One2many('product.image', 'product_request_lines_id', string="Extra Product Media", copy=True)
    wk_product_tab_ids = fields.One2many(
        'wk.product.tabs', 'tab_product_template_id', string='Product Tabs', domain=['|',('active','=',True),('active','=',False)],)
    
    product_variant_count = fields.Integer(
        '# Product Variants', compute='_compute_product_variant_count')
    
    
    def _compute_product_variant_count(self):
        for request in self:
            # do not pollute variants to be prefetched when counting variants
            request.product_variant_count = len(request.with_prefetch().attribute_line_ids)
    
    
    
    def change_product_qty(self,product_obj):
        if self.product_variant_count == 0:
            for request in self:
                for product in product_obj:                            
                    location_id = self.env['ir.config_parameter'].sudo().get_param('custom_inventory_forms.location_id')
                    quants = {
                            'product_id': product.id,
                            'inventory_quantity': request.product_qty,
                            'location_id': int(location_id),                   
                        }
                    self.env['stock.quant'].sudo().with_context(inventory_mode=True).create(quants)      
        
   
   
        
    
    @api.constrains('price')
    def price_constratints(self):
        if self.price == 0.00 :
            raise UserError('Price must be different from zero')
        price = str(self.price)
        if len(price) > 9 :
            raise UserError('Invalid Price')
        if self.price < 0:
                raise UserError("Price cannot be negative.")
            
        
    @api.constrains('product_qty')
    def product_qty_constratints(self):
        if self.product_variant_count == 0:
            if self.product_qty == 0 :
                raise UserError('Qty must be different from zero') 
            if self.product_qty < 0:
                raise UserError("Quantity cannot be negative.")       
            product_qty = str(self.product_qty)
            if len(product_qty) > 3 :
                raise UserError('Invalid Qty')
   

    @api.model
    def create(self, vals):
        obj = super(ProductRequestLine, self).create(vals)
        if obj.product_id == '-':
            sequence = self.env['ir.sequence'].get(
                'product.ref.seq') or '-'
            obj.write({'product_id': sequence})
        return obj  
    
    
    
    
    

class ProductImage(models.Model):
    _inherit = 'product.image'
  
    product_request_lines_id = fields.Many2one('product.request.line', string='Product')

class ProductRequestAttributeLine(models.Model):
    _name = 'product.request.attribute.line'
    _description = 'Product Request Attribute Line'
    
    active = fields.Boolean(default=True)
    product_request_line_id = fields.Many2one('product.request.line', string="Product Request Line", ondelete='cascade', required=True, index=True)
    attribute_id = fields.Many2one('product.attribute', string="Attribute",  required=True)
    value_ids = fields.Many2many('product.attribute.value', string="Values", domain="[('attribute_id', '=', attribute_id)]", ondelete='restrict')
    
class WkProductTabs(models.Model):
    _inherit = 'wk.product.tabs'
    
    tab_product_template_id  = fields.Many2one('product.request.line',string='Product')
        
    
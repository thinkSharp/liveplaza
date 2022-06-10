# https://www.odoo.com/forum/help-1/write-method-not-working-trying-to-update-values-in-one2many-field-117196

from odoo import fields, models, api, _, exceptions
import datetime


class ProductTemplateAttributeLineInherit(models.Model):
    _inherit = "product.template.attribute.line"
    requested_service_product_tmpl_id = fields.Many2one('service.request.product')



class ServiceProductRequest(models.Model):
    _name = 'service.request'
    _description = 'Service Product Requests from vendors to sale on website.'
    
    name = fields.Char(string='Request', required=True, copy=False, index=True, readonly=True, default=lambda self: _('New'))
    state = fields.Selection([
        ('draft', 'Draft'),
        ('requested', 'Requested'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ], string='Status', readonly=True, copy=False, index=True, default='draft')

    seller = fields.Many2one("res.partner", string="Seller", default=lambda self: self.env.user.partner_id.id if self.env.user.partner_id and self.env.user.partner_id.seller else self.env['res.partner'], required=True)
    product_ids = fields.One2many('service.request.product', 'product_request_id', string='Service Products')
    no_products = fields.Integer(readonly=True, default=0)


    def action_request(self):
        super(ServiceProductRequest, self).write({'state': 'requested'})

        product_tmpl_ids_query = "select product_tmpl_id from service_request_product where product_request_id=%s"
        self.env.cr.execute(product_tmpl_ids_query, (self.id,))
        product_tmpl_ids = self.env.cr.fetchall()

        for product_tmpl_id in product_tmpl_ids:
            print('Product template Id', product_tmpl_id)
            self.env["product.template"].search([('id', '=', product_tmpl_id)]).write({'status': 'pending'})
            '''
            product_query = "select id from product_product where product_tmpl_id=%s"
            self.env.cr.execute(product_query, (product_tmpl_id,))
            product_ids = self.env.cr.fetchall()
            print('Products:', product_ids)
            for product_id in product_ids:
                self.env["product.product"].search([('id', '=', product_id)]).write({'state': 'requested'})
            '''


        return True

    def action_approve(self):
        super(ServiceProductRequest, self).write({'state': 'approved'})

        product_tmpl_ids_query = "select product_tmpl_id from service_request_product where product_request_id=%s"
        self.env.cr.execute(product_tmpl_ids_query, (self.id,))
        product_tmpl_ids = self.env.cr.fetchall()

        for product_tmpl_id in product_tmpl_ids:
            print('Product Delete..........................')
            print('Product template Id', product_tmpl_id)
            self.env["product.template"].search([('id', '=', product_tmpl_id)]).write({'status': 'approved', 'sale_ok': True})
            '''
            product_query = "select id from product_product where product_tmpl_id=%s"
            self.env.cr.execute(product_query, (product_tmpl_id,))
            product_ids = self.env.cr.fetchall()
            print('Products:', product_ids)
            for product_id in product_ids:
                self.env["product.product"].search([('id', '=', product_id)]).write({'state': 'approved'})
            '''
        return True


    def action_reject(self):
        super(ServiceProductRequest, self).write({'state': 'rejected'})

        product_tmpl_ids_query = "select product_tmpl_id from service_request_product where product_request_id=%s"
        self.env.cr.execute(product_tmpl_ids_query, (self.id,))
        product_tmpl_ids = self.env.cr.fetchall()

        for product_tmpl_id in product_tmpl_ids:
            print('Product Delete..........................')
            print('Product template Id', product_tmpl_id)
            self.env["product.template"].search([('id', '=', product_tmpl_id)]).write({'status': 'rejected'})
            '''
            product_query = "select id from product_product where product_tmpl_id=%s"
            self.env.cr.execute(product_query, (product_tmpl_id,))
            product_ids = self.env.cr.fetchall()
            print('Products:', product_ids)
            for product_id in product_ids:
                self.env["product.product"].search([('id', '=', product_id)]).write({'state': 'rejected'})
            '''
        return True

    @api.constrains('product_ids')
    def _check_product_ids(self):
        print(len(self.product_ids))
        self.no_products = len(self.product_ids)
        missing_is_product_saved = []
        missing_is_variants_generated = []
        missing_is_variants_saved = []
        missing_is_extra_price_saved = []
        for product_id in self.product_ids:
            if product_id.has_variant == 'yes':
                if not product_id.is_variants_generated:
                    missing_is_variants_generated.append(product_id.name)

                if not product_id.is_variants_saved:
                    missing_is_variants_saved.append(product_id.name)

                if not product_id.is_extra_price_saved:

                    missing_is_extra_price_saved.append(product_id.name)

            elif product_id.has_variant == 'no':
                if not product_id.is_product_saved:
                    missing_is_product_saved.append(product_id.name)


        if missing_is_product_saved or missing_is_variants_generated or missing_is_variants_saved or missing_is_extra_price_saved:
            string = ''
            if missing_is_product_saved:
                string += ' Generate Product:\n'
                for product in missing_is_product_saved:
                    string += f'     {product}\n'

            if missing_is_variants_generated:
                string += ' Generate Variants:\n'
                for product in missing_is_variants_generated:
                    string += f'     {product}\n'

            if missing_is_variants_saved:
                string += ' Save Variants:\n'
                for product in missing_is_variants_saved:
                    string += f'     {product}\n'

            if missing_is_extra_price_saved:
                string += ' Save Extra Price:\n'
                for product in missing_is_extra_price_saved:
                    string += f'     {product}\n'


            raise exceptions.ValidationError(_('Before Saving,\n' + string))


    @api.model
    def create(self, vals):
        if vals.get('name', _('New')) == _('New'):
            vals['name'] = self.env['ir.sequence'].next_by_code('service.request.sequence') or _('New')
        result = super(ServiceProductRequest, self).create(vals)
        return result






class ServiceProduct(models.Model):


    @api.model
    def _get_default_attribute(self):
        terms_obj = self.env['product.template.attribute.value']
        termsids = terms_obj.search([('product_tmpl_id', '=', self.product_tmpl_id)])

        return termsids




    _name = "service.request.product"
    _description = "Service Products"

    name = fields.Char(required=True, string='Service Product Name')
    categ_ids = fields.Many2many('product.public.category', string='Product Category', required=True)
    list_price = fields.Float(required=True, string='Product Price')
    quantity = fields.Integer(required=True, string='Product Quantity')
    image_1920 = fields.Image(required=True, string='Product Image 1')
    image2 = fields.Image(string='Product Image 2')
    image3 = fields.Image(string='Product Image 3')
    image4 = fields.Image(string='Product Image 4')
    image5 = fields.Image(string='Product Image 5')
    # video = fields.Video()
    alternative = fields.Many2many('product.template', string='Alternative Products')
    description = fields.Html(string='Product Description')
    returnable = fields.Boolean(readonly=True, default=True)
    auto_publish = fields.Boolean(readonly=True, default=True)
    product_request_id = fields.Many2one('service.request', ondelete='cascade')
    admin_request_id = fields.Many2one('service.admin.product.request', ondelete='cascade')

    attribute_line_ids = fields.One2many('product.template.attribute.line', 'requested_product_tmpl_id', string='Variants')
    product_variant_lines = fields.One2many('service.request.product.variant.lines', 'product_variant_id', string='Products', required=True)
    seller = fields.Many2one("res.partner", string="Seller", default=lambda self: self.env.user.partner_id.id if self.env.user.partner_id and self.env.user.partner_id.seller else self.env['res.partner'])

    has_variant = fields.Selection([
        ('yes', 'Yes'),
        ('no', 'No'),
    ], string='Has Variants?', copy=False, index=True, required=True)
    product_tmpl_id = fields.Integer()

    is_generate_button_pressed = fields.Boolean(default=False)
    is_variants_generated = fields.Boolean(default=False)
    is_product_saved = fields.Boolean(default=False)
    is_variants_saved = fields.Boolean(defalut=False)
    is_extra_price_saved = fields.Boolean(defalut=False)
    product_template_attribute_value_ids = fields.Many2many(
        'product.template.attribute.value',
        domain="[('product_tmpl_id', '=', product_tmpl_id)]",
        string='Variant Extra Price',
    default=_get_default_attribute)

    def action_generate_product_variants(self):

        if not self.is_generate_button_pressed:

            for line in self:
                if line.quantity > 999 or line.quantity < 1:
                    raise exceptions.ValidationError(_('Quantity must be between 1 and 999.'))
                    return True



                if line.list_price > 9999999 or line.list_price< 100:
                    raise exceptions.ValidationError(_('Price must be between 100 and 9999999.'))
                    return True



            if self.has_variant == 'yes':
                if not len(self.attribute_line_ids):
                    raise exceptions.ValidationError(_('Add Variants!'))

            for line in self:
                vals = {
                    'name': line.name,
                    'categ_id': 1,
                    'list_price': line.list_price,
                    'image_1920': line.image_1920,
                    'image2': line.image2,
                    'image3': line.image3,
                    'image4': line.image4,
                    'image5': line.image5,
                    'alternative': line.alternative,
                    'description': line.description,
                    'returnable': line.returnable,
                    'auto_publish': line.auto_publish,
                    'product_request_id': line.product_request_id,
                }
                # print('action_variant_vals', vals)


                product_vals = {
                    'name': vals['name'],
                    'categ_id': 1,
                    'type': 'product',
                    'list_price': vals['list_price'],
                    'image_1920': vals['image_1920'],
                    'description': vals['description'],
                    'active': True,
                    'sale_ok': False,
                    'website_published':vals['auto_publish'],
                    'public_categ_ids': line.categ_ids,
                    'invoice_policy': 'order',
                    'alternative_product_ids': vals['alternative'],
                    'inventory_availability': 'always',
                    'is_service': True

                }

                product_tmpl_obj = self.env['product.template'].create(product_vals)
                if product_tmpl_obj:
                    self.write({'is_variants_generated' : True})
                # print('Action Variant New Product:', product_tmpl_obj.id)
                self.product_tmpl_id = product_tmpl_obj.id

                self.env['wk.product.tabs'].create({'name': 'Product Description', 'content': line.description,'tab_product_id': self.product_tmpl_id, 'active': True})

                for image in [line.image2, line.image3, line.image4, line.image5]:
                    if image:
                        self.env['product.image'].create({'name': self.name, 'image_1920': image, 'product_tmpl_id': self.product_tmpl_id})

                for att_data in line:
                    for att_line in att_data.attribute_line_ids:
                        lines ={
                        'attribute_id': att_line.attribute_id.id,
                        'product_tmpl_id': product_tmpl_obj.id,
                        'value_ids': [(6, 0, att_line.value_ids.ids)]
                        }
                        self.env['product.template.attribute.line'].create(lines)

            product_obj =self.env['product.product'].search([('product_tmpl_id', '=', self.product_tmpl_id)])
            for pobj in product_obj:
                self.env['service.request.product.variant.lines'].sudo().create({
                    'product_id': pobj.id,
                    'product_variant_id': self.id,
                    'price': pobj.lst_price,
                    'image': self.image_1920,
                    'quantity': self.quantity
                })

            #terms_obj = self.env['product.template.attribute.value']
            #termsids = terms_obj.search([('product_tmpl_id', '=', self.product_tmpl_id)])
            #self.product_template_attribute_value_ids = [(4, 0, termsid) for termsid in termsids]




            if self.has_variant == 'no':
                warehouse_location = self.env['ir.config_parameter'].sudo().get_param('multi_product_request.warehouse_location')

                print('Warehouse Location', warehouse_location)

                for line in self.product_variant_lines:

                    lines ={
                        'location_id': int(warehouse_location),
                        'product_id': line.product_id.id,
                        'in_date': datetime.datetime.today(),
                        'quantity': line.quantity
                    }

                    print('Line', lines)
                    self.env['stock.quant'].sudo().create(lines)

                    self.write({'is_variants_generated': False})
                    self.write({'is_product_saved': True})

            self.write({'is_generate_button_pressed': True})
            return True
        



    def saved_variants(self):
        for line in self.product_variant_lines:
            print('In upper validation')
            print(line.quantity)
            print(line.price)

            if line.quantity > 999 or line.quantity < 1:
                raise exceptions.ValidationError(_('Quantity must be between 1 and 999.'))
                return True




            if line.price > 9999999 or line.price < 100:
                raise exceptions.ValidationError(_('Price must be between 100 and 9999999.'))
                return True

        warehouse_location = self.env['ir.config_parameter'].sudo().get_param('multi_product_request.warehouse_location')
        for index,line in enumerate(self.product_variant_lines):
            print('In Loop.............................')
            print('IN UPDATE VARIANT FOR LOOP')
            lines ={
                'location_id': int(warehouse_location),
                'product_id': line.product_id.id,
                'in_date': datetime.datetime.today(),
                'quantity': line.quantity
            }

            print('Line', lines)
            self.env['stock.quant'].sudo().create(lines)
            self.write({'is_variants_saved': True})



            self.env['product.product'].search([('id', '=', line.product_id.id)]).write({'image_1920': line.image})





        return True



    def action_save_extra_price(self):
        self.write({'is_extra_price_saved': True})
        for variant in self.product_variant_lines:
            variant.price = self.env['product.product'].search([('id', '=', variant.product_id.id)]).lst_price












class Product_Variants_Lines(models.Model):
    _name = "service.request.product.variant.lines"
    _description = "Product Variants Request"

    
    product_variant_id = fields.Many2one('service.request.product', string='Products')
    product_id = fields.Many2one('product.product', readonly=True)
    quantity = fields.Integer()
    price = fields.Float(readonly=True)
    image = fields.Image()

    def unlink(self):
        for line in self:
            print('Delete Product', line.product_id.id)
            self.env['product.product'].search([('id', '=', line.product_id.id)]).unlink()

        return super(Product_Variants_Lines, self).unlink()




class AdminProductRequest(models.Model):
    _name = 'service.admin.product.request'
    _description = 'Product requests from admin as a vendor to sale on website.'

    name = fields.Char(string='Request', required=True, copy=False, index=True, readonly=True,
                       default=lambda self: _('New'))

    state = fields.Selection([
        ('draft', 'Draft'),
        ('approved', 'Approved'),
    ], string='Status', readonly=True, copy=False, index=True, default='draft')
    seller = fields.Many2one("res.partner", string="Seller", default=lambda self: self.env.user.partner_id.id if self.env.user.partner_id and self.env.user.partner_id.seller else self.env['res.partner'])

    product_ids = fields.One2many('product.request.product', 'admin_request_id', string='Products')
    no_products = fields.Integer(readonly=True, default=0)


    def action_approve(self):
        super(AdminProductRequest, self).write({'state': 'approved'})

        product_tmpl_ids_query = "select product_tmpl_id from product_request_product where admin_request_id=%s"
        self.env.cr.execute(product_tmpl_ids_query, (self.id,))
        product_tmpl_ids = self.env.cr.fetchall()
        print(product_tmpl_ids)

        for product_tmpl_id in product_tmpl_ids:
            print('Product Delete..........................')
            print('Product template Id', product_tmpl_id)
            self.env["product.template"].search([('id', '=', product_tmpl_id)]).write({'status': 'approved', 'sale_ok': True, 'marketplace_seller_id': self.seller.id})

        return True

    @api.constrains('product_ids')
    def _check_product_ids(self):
        print(len(self.product_ids))
        self.no_products = len(self.product_ids)
        missing_is_product_saved = []
        missing_is_variants_generated = []
        missing_is_variants_saved = []
        missing_is_extra_price_saved = []
        for product_id in self.product_ids:

            if product_id.has_variant == 'yes':

                if not product_id.is_variants_generated:
                    missing_is_variants_generated.append(product_id.name)

                if not product_id.is_variants_saved:
                    missing_is_variants_saved.append(product_id.name)


                if not product_id.is_extra_price_saved:

                    missing_is_extra_price_saved.append(product_id.name)


            elif product_id.has_variant == 'no':
                if not product_id.is_product_saved:
                    missing_is_product_saved.append(product_id.name)


        if missing_is_product_saved or missing_is_variants_generated or missing_is_variants_saved or missing_is_extra_price_saved:
            string = ''
            if missing_is_product_saved:
                string += ' Generate Product:\n'
                for product in missing_is_product_saved:
                    string += f'     {product}\n'

            if missing_is_variants_generated:
                string += ' Generate Variants:\n'
                for product in missing_is_variants_generated:
                    string += f'     {product}\n'

            if missing_is_variants_saved:
                string += ' Save Variants:\n'
                for product in missing_is_variants_saved:
                    string += f'     {product}\n'

            if missing_is_extra_price_saved:
                string += ' Save Extra Price:\n'
                for product in missing_is_extra_price_saved:
                    string += f'     {product}\n'



            raise exceptions.ValidationError(_('Before Saving,\n' + string))

    @api.onchange('seller')
    def _onchange_seller(self):
        print('Before Seller', self.seller)
        seller = self.seller
        self.product_ids.unlink()
        self.seller = seller
        print('After Seller', self.seller)







    @api.model
    def create(self, vals):
        if vals.get('name', _('New')) == _('New'):
            vals['name'] = self.env['ir.sequence'].next_by_code('request.sequence') or _('New')
        result = super(AdminProductRequest, self).create(vals)
        return result
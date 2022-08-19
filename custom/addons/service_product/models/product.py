from odoo import fields, models, api, _, exceptions
from odoo.addons.http_routing.models.ir_http import slug


class ProductInherit(models.Model):
    _inherit = 'product.template'

    is_service = fields.Boolean(string="Service Type", default=False)
    expiration_policy = state = fields.Selection([
        ('0', 'No expired'),
        ('1', '1 day'),
        ('7', '7 days'),
        ('30', '30 days'),
        ('90', '90 days'),
        ('180', '180 days'),
        ('365', '365 days'),
    ], string='Expiration Policy', default='0')

    def delete_discard_products(self):
        pending_products = self.env["product.template"].search([('status', '=', "draft"), ('type', '=', "product")])
        print("Pending Products..........", pending_products)
        for pending_product in pending_products:
            if not self.env['service.request.product'].search([('product_tmpl_id', '=', pending_product.id)]):
                products = self.env['product.product'].search([('product_tmpl_id', '=', pending_product.id)])

                for product in products:
                    stock_quants = self.env['stock.quant'].search([('product_id', '=', product.id)])
                    for stock_quant in stock_quants:
                        stock_quant.unlink()
                    product.unlink()

    def _compute_website_url(self):
        super(ProductInherit, self)._compute_website_url()
        for product in self:
            if product.is_service or product.type == 'service':
                product.website_url = "/service/%s" % slug(product)

            else:
                product.website_url = "/shop/product/%s" % slug(product)
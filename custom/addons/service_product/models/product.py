from odoo import fields, models, api, _, exceptions


class ProductInherit(models.Model):
    _inherit = 'product.template'

    is_service = fields.Boolean(string="Service Type", default=False)

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

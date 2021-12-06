# -*- coding: utf-8 -*-

from odoo import fields, models, api, _
import pyperclip as pc 

class ProductTemplate(models.Model):
    _inherit = "product.template"

    def product_info_copy(self):
        for product in self:
            base_url = self.env['ir.config_parameter'].get_param('web.base.url')
            base_url += str(product.website_url)

            product_info = 'Item : ' + \
                str(product.name) + '\n' + 'Code : ' + \
                str(product.barcode) + '\n' + 'Price : ' + \
                str(product.currency_id.symbol) + ' ' + str(product.lst_price) + '\n' + '\n' + 'Buy Here : ' + str(base_url)
            
            pc.copy(product_info)
            spam = pc.paste()

            return spam

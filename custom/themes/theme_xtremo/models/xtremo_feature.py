# -*- coding: utf-8 -*-
#################################################################################
#
#   Copyright (c) 2018-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>)
#   See LICENSE URL <https://store.webkul.com/license.html/> for full copyright and licensing details.
#################################################################################
import logging

from odoo import api, fields, models, tools
import base64
import os


_logger = logging.getLogger(__name__)

class XtremoFeatured(models.Model):
    _name = 'xtremo.featured'
    _description = "Xtremo Features"

    name = fields.Char(string="Name", require=True, translate=True)
    type = fields.Selection(selection=[('product','Products'),('category','Categories'),('top_rating','Top Rating'), ('price_list','Top Sale')], string="Type", require=True)
    product_ids = fields.Many2many(string="Products",comodel_name="product.template")
    category_ids = fields.Many2many(string="Categories",comodel_name="product.public.category")
    price_list = fields.Many2one(string="Price List", comodel_name="product.pricelist")
    is_publish = fields.Boolean(string="Publish", default=False)
    avg_rating = fields.Integer(string="Average Rating", default=2)
    no_of_products = fields.Integer(string="No Of Products On Website", default=10)

    # @api.multi
    def toggle_is_publish(self):
        is_active = False
        is_price_list = False
        if self.type != 'price_list':
            is_active = self.env['xtremo.featured'].search([('is_publish','=',True),('type', '=', self.type)])
        elif self.type == 'price_list':
            is_price_list = True
            is_active = self.env['xtremo.featured'].search([('is_publish','=',True),('price_list', '=', self.price_list.id)])
        if not is_active.id == self.id and is_active:
            template = self.env.ref('theme_xtremo.xtremo_featured_wizard_from_view').id
            wizards = self.env['xtremo.featured.wizards'].create({
                "xtremo_featured": is_active.id,
                'is_price_list': is_price_list
            })
            return {
                    "type" : "ir.actions.act_window",
                    "res_model" : "xtremo.featured.wizards",
                    "view_mode" : "form",
                    'view_type': 'form',
                    "view_id" : template,
                    "res_id" : wizards.id,
                    "target" : "new"
                    }
        else:
            self.is_publish = not self.is_publish
        return True

    @api.onchange('type')
    def type_change(self):
        self.product_ids = []
        if self.type == 'product':
            return {
                'domain': {'product_ids': [('id', '!=', False)]}
            }


    @api.onchange('price_list')
    def price_list_onchange(self):
        price_list_id = self.price_list
        self.product_ids = []
        products = []
        features = self.env['xtremo.featured'].search([('is_publish','=',True),('price_list', '=', self.price_list.id), ('type', '=', 'price_list')])
        if features:
            self.is_publish = False
        for price in price_list_id.item_ids:
            if price.applied_on == '3_global':
                return {
                    'domain': {'product_ids': [('id', '!=', False)]}
                }
            if price.product_tmpl_id:
                products = products+price.product_tmpl_id.ids
            if price.product_id:
                products = products+list(price.product_id.mapped('product_tmpl_id').ids)
            if price.categ_id:
                products = products+self.env['product.template'].search([('categ_id', '=', price.categ_id.id)]).ids
        return {
            'domain': {'product_ids': [('id', 'in', list(set(products)))]}
        }

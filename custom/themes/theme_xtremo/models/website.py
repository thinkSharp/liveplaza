    # -*- coding: utf-8 -*-
#################################################################################
#
#   Copyright (c) 2018-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>)
#   See LICENSE URL <https://store.webkul.com/license.html/> for full copyright and licensing details.
#################################################################################
import logging
import math

from odoo import api, fields, models, tools
from odoo.http import request
from odoo.addons.http_routing.models.ir_http import slug
from odoo.addons.website.controllers.main import QueryURL
from odoo.addons.http_routing.models.ir_http import slug
from odoo.osv import expression

_logger = logging.getLogger(__name__)


class Website(models.Model):
    _inherit = 'website'

    login_background = fields.Binary(string="Login Page Background")

    def get_all_categories_url(self, category):
        url = "/shop"
        if len(category)>0:
            url = "/shop/category/%s" % slug(category)
        return url

    def get_all_categories(self):
        keep = QueryURL("/", category=0)
        return {
            'keep': keep
        }

    def get_all_featured_products(self):
        xtremo_featured = self.env['xtremo.featured'].sudo()
        featured_products = xtremo_featured.search([('is_publish', '=', True), ('type', '=', 'product')])
        if featured_products:
            return featured_products
        return False

    def get_all_category_products(self):
        xtremo_featured = self.env['xtremo.featured'].sudo()
        featured_products = xtremo_featured.search([('is_publish', '=', True), ('type', '=', 'category')])
        return featured_products

    def get_all_top_listed_products(self):
        config = self.env['xtremo.featured'].sudo().search([('type', '=', 'top_rating'),('is_publish', '=', True)])
        total_products = []
        name = "Top Rated Products"
        if config:
            average_rating = config.avg_rating
            limit = config.no_of_products
            total_products = self.env['product.template'].sudo().search([
                    ("website_published", "=", True),
                    ('xtremo_avg_rating', '>=', average_rating)], limit=limit)
            name = config.name

        if not total_products:
            total_products = self.env['product.template'].sudo().search([
                    ("website_published", "=", True)], limit=6)
        return {
                "name": (name or "Top Rated Products"),
                "featured_products": total_products
                }

    def get_all_top_sale_products(self):
        xtremo_featured = self.env['xtremo.featured'].sudo()
        price_list_id = self.env['res.users'].sudo().browse(request._uid).property_product_pricelist
        featured_products = xtremo_featured.search([('is_publish', '=', True), ('type', '=', 'price_list'), ('price_list', '=', price_list_id.id)])
        return featured_products

    def get_product_rating(self, product=False):
        res = {}
        if product and product.xtremo_avg_rating:
            val = product.xtremo_avg_rating
            decimal = (val - math.floor(val))
            decimal = round(decimal,1)
            if decimal == .5:
                val = math.floor(val) + .5
            elif (decimal < .3) or (decimal > .7):
                val = round(val)
            else:
                val = math.floor(val) + .5
            res.update({
                'val_integer': math.floor(val),
                'val_decimal':  val - math.floor(val),
                'empty_star':  5 - ( math.floor(val)+math.ceil(val - math.floor(val))),
                'count': product.total_start_rating_count
            })

        return res


    @api.model
    def payment_icons(self):
        order = request.website.sale_get_order(force_create=True)
        domain = expression.AND([
            ['&', ('state', 'in', ['enabled', 'test']), ('company_id', '=', order.company_id.id)],
            ['|', ('website_id', '=', False), ('website_id', '=', request.website.id)],
            ['|', ('country_ids', '=', False), ('country_ids', 'in', [order.partner_id.country_id.id])]
        ])
        acquirers = request.env['payment.acquirer'].search(domain)

        icons = set()
        acq = [icons.add(acq.payment_icon_ids) for acq in acquirers if (acq.payment_flow == 'form' and acq.view_template_id) or
                                (acq.payment_flow == 's2s' and acq.registration_view_template_id)]
        icon = {}
        if icons:
            icon = icons.pop()
            for i in icons:
                icon += i
        return set(icon)

class ProductTemplate(models.Model):
    _inherit = "product.template"

    def _get_avg_rating(self):
        for record in self:
            if not (record.total_start_rating_count and record.xtremo_avg_rating):
                rating = 0
                total = 0
                for x in record.rating_ids:
                    if x.rating:
                        total += 1
                        rating += x.rating/2
                _logger.info(total, rating)
                record.total_start_rating_count = total
                record.xtremo_avg_rating = rating/total if total and rating else 0.0

    def get_active_slide_image(self):
        active_image = self.product_template_image_ids.filtered(lambda image: image.set_slider_on_shop)
        if not active_image.exists() and self.product_template_image_ids.exists():
            active_image = self.product_template_image_ids[0]
        if not active_image.exists():
            active_image = False
        return active_image

    total_start_rating_count = fields.Integer(string='Total Start Rating Count', compute='_get_avg_rating', store=True, default=0)
    xtremo_avg_rating = fields.Float(string='Avg Rating', compute='_get_avg_rating', store=True, default=0)


class ProductImage(models.Model):
    _inherit = "product.image"

    set_slider_on_shop = fields.Boolean(string="Product Slider On Website", default=False)

    def set_unselected(self, vals):
        if vals.get("set_slider_on_shop"):
            product = False
            if vals.get("product_tmpl_id"):
                product = vals.get("product_tmpl_id")
            else:
                product = self.product_tmpl_id.id
            product = self.env['product.template'].browse(product)
            for image in product.product_template_image_ids:
                image.set_slider_on_shop = False

    @api.model
    def create(self, values):
        self.set_unselected(values)
        res = super(ProductImage, self).create(values)
        return res

    def write(self, values):
        self.set_unselected(values)
        res = super(ProductImage, self).write(values)
        return res


class ProductPublicCategory(models.Model):
    _inherit = "product.public.category"

    icon = fields.Binary(string="Icon", help="Icon for the xtremo mega menu")

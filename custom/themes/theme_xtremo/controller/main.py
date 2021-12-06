# -*- coding: utf-8 -*-
#################################################################################
#
#   Copyright (c) 2018-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>)
#   See LICENSE URL <https://store.webkul.com/license.html/> for full copyright and licensing details.
#################################################################################
import logging

from odoo import fields, http, tools, _
from odoo.http import route, request
from odoo.addons.website_sale.controllers.main import WebsiteSale
from odoo.addons.website.controllers.main import Website
from odoo.addons.portal.controllers.mail import PortalChatter
from odoo.addons.website.controllers.main import QueryURL
from odoo.addons.http_routing.models.ir_http import slug

_logger = logging.getLogger(__name__)


class WebsiteSale(WebsiteSale):


    def get_all_categories(self, category, cate_list=[], url=False, key=1):
        try:
            id = int(category)
            category = request.env['product.public.category'].browse(id)
        except ValueError:
            category = category
        cate_list.append({"name": category.name, "url": url, "key": key})
        if len(category.parent_id)>0:
            url = "/shop/category/%s" % slug(category.parent_id)
            self.get_all_categories(category.parent_id, cate_list, url, key+1)
        return sorted(cate_list, key = lambda i: i.get('key') if i.get('key') else True, reverse=True)

    def get_price_filer_domain(self, min="", max=""):
        res = {}
        ICPSudo = request.env['ir.default'].sudo()
        min_limit = ICPSudo.get('xtremo.res.config.settings', 'website_min_price_filter') or 0
        max_limit = ICPSudo.get('xtremo.res.config.settings', 'website_max_price_filter') or 100000
        res["min_limit"] = min_limit
        res["max_limit"] = max_limit
        res["min-price"] = min if min and int(min) >= 0 else min_limit
        res["max-price"] = max if max else max_limit
        url = request.httprequest.full_path
        prev_1 = "min_price="+str(min)
        prev_2 = "max_price="+str(max)
        if (prev_1 in url) and (prev_2 in url):
            url = url.replace(prev_1, "min_price=xtremo-lower-val")
            url = url.replace(prev_2, "max_price=xtremo-higher-val")
        elif ("?" in url) and (str(min) not in url) and (str(max) not in url):
            url = "{}&min_price={}&max_price={}".format(url, "xtremo-lower-val", "xtremo-higher-val")
        else:
            url = "{}?min_price={}&max_price={}".format(url, "xtremo-lower-val", "xtremo-higher-val")
        res['filter-url'] = url
        return res

    def _get_search_domain(self, search, category, attrib_values):
        domain = super(WebsiteSale, self)._get_search_domain(search, category, attrib_values)
        min_price = request.httprequest.args.get('min_price')
        max_price = request.httprequest.args.get('max_price')
        if min_price and max_price:
            domain.append(('lst_price','>=',min_price))
            domain.append(('lst_price','<=',max_price))
        return domain

    @route(['/xtremo/get-feature'], type="json", website=True, auth="public")
    def get_feature(self, ref=False, **post):
        template = False
        t_name = False
        xt_products = False
        if ref == "feature":
            t_name = "theme_xtremo.xtremo_home_page_feature"
            xt_products = request.website.get_all_featured_products()
        elif ref == "category":
            t_name = "theme_xtremo.xtremo_home_page_category"
            xt_products = request.website.get_all_category_products()
        elif ref == "top_sale":
            t_name = "theme_xtremo.xtremo_home_page_top_sales"
            xt_products = request.website.get_all_top_sale_products()
        elif ref == "top_rated":
            t_name = "theme_xtremo.xtremo_home_page_top_rated"
            xt_products = request.website.get_all_top_listed_products()
        if t_name:
            template = request.env['ir.ui.view'].render_template(t_name, {"xt_products": xt_products})
        return template

    @route(['/xtremo/get-category-feature'], type="json", website=True, auth="public")
    def get_category_feature(self, ref=False, **post):
        template = request.env['ir.ui.view'].render_template('theme_xtremo.xtremo_banner_with_category_item', {})
        return template

    @http.route([
        '''/shop''',
        '''/shop/page/<int:page>''',
        '''/shop/category/<model("product.public.category"):category>''',
        '''/shop/category/<model("product.public.category"):category>/page/<int:page>'''
    ], type='http', auth="public", website=True)
    def shop(self, page=0, category=None, search='', ppg=False, **post):
        result = super(WebsiteSale, self).shop(page=page, category=category, search=search, ppg=ppg, **post)
        values = result.qcontext

        if values.get("pager").get('page_end').get('num') < page :
            return "none"
        elif post.get("test"):
            view = request.render("theme_xtremo.wk_lazy_list_product_item", values)
            return view

        attrib_list = request.httprequest.args.getlist('attrib')
        min_price = post.get('min_price')
        max_price = post.get('max_price')
        keep = QueryURL('/shop', category=category and int(category), search=search, attrib=attrib_list, order=post.get('order'), min_price=min_price, max_price=max_price)
        category_list = []
        if category:
            category_list = self.get_all_categories(category=category, cate_list=[], url=False)
        if not category_list:
            category_list = [{"name": "All Products"}]

        price_filter_config = self.get_price_filer_domain(min_price,max_price)
        result.qcontext.update({
            'all_categories': category_list,
            "filter_price": price_filter_config,
            'ppg': request.env['website'].get_current_website().shop_ppg,
            'keep': keep,
        })
        return result


class XtremoWebsiteRating(PortalChatter):

    @route()
    def portal_chatter_post(self, res_model, res_id, message, **kw):
        result = super(XtremoWebsiteRating, self).portal_chatter_post(res_model, res_id, message, **kw)
        if res_model == 'product.template' and kw.get('rating_value') and message:
            product = request.env['product.template'].sudo().browse(int(res_id))
            if product.exists():
                rate = 0
                try:
                    rate = float(kw.get('rating_value'))
                except Exception as e:
                    rate = 0
                if product.xtremo_avg_rating and rate:
                    rate = rate/2
                    increment = (rate - product.xtremo_avg_rating)/(product.total_start_rating_count +1)
                    product.xtremo_avg_rating += increment
                    product.total_start_rating_count += 1
                else:
                    rating = 0
                    total = 0
                    for x in product.rating_ids:
                        if x.rating:
                            total += 1
                            rating += x.rating/2
                    product.total_start_rating_count = total
                    product.xtremo_avg_rating = rating/total if total and rating else 0.0
        return result

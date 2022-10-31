# -*- coding: utf-8 -*- --

from odoo import fields, http, tools, _
from odoo.http import request
from odoo.osv import expression
from werkzeug.exceptions import Forbidden, NotFound
from odoo.addons.website.controllers.main import QueryURL

from odoo.addons.website_sale.controllers.main import WebsiteSale as Website_Sale
from odoo.addons.website.controllers.main import Website
from odoo.exceptions import except_orm, Warning, RedirectWarning, UserError
from odoo.addons.http_routing.models.ir_http import slug
from odoo.addons.website_sale.controllers.main import TableCompute
import random

class WebsiteSale(Website_Sale):
    
    def _get_mandatory_billing_fields(self):
        return ["name", "street", "country_id","township_id"]

    def _get_mandatory_shipping_fields(self):
        return ["name", "street",  "country_id","township_id"]

    def _get_search_order(self, post):
        order = post.get('order') or 'website_sequence DESC'
#         or 'qty_available ASC'
        return 'is_published desc, %s, id desc' % order

    def _get_search_faq_domain(self, search):
        domains = []
        if search:
            for srch in search.split(" "):
                subdomains = [
                    [('question', 'ilike', srch)],
                    [('answer', 'ilike', srch)],
                    [('question_myanmar', 'ilike', srch)],
                    [('answer_myanmar', 'ilike', srch)]
                ]
                domains.append(expression.OR(subdomains))
        domains.append([('website_published', '=', True)])

        return expression.AND(domains)

    # def get_deals_domain(self):
    #     domain = []
    #     subdomain = [
    #         [('state', '=', 'validated')],
    #         [('state', '=', 'expired')]
    #     ]
    #     domain.append(expression.OR(subdomain))
    #     domain.append()


    
#     @http.route(['/shop/address'], type='http', methods=['GET', 'POST'], auth="public", website=True, sitemap=False)
#     def address(self, **kw):
#         if  kw.get("name",False):
#             township_id = kw.get("township_id")
#             if township_id == None:
#                 raise Warning(_("Quantity cannot be negative."))
#             values=super(WebsiteSale,self).address(**kw)
#         return values

    def _checkout_form_save(self, mode, checkout, all_values):
        Partner = request.env['res.partner']

        township_id = all_values.get('township_id')

        checkout.update({'township_id': township_id})

        if mode[0] == 'new':
            partner_id = Partner.sudo().with_context(
                tracking_disable=True).create(checkout).id
        elif mode[0] == 'edit':
            partner_id = int(all_values.get('partner_id', 0))
            if partner_id:
                # double check
                order = request.website.sale_get_order()
                shippings = Partner.sudo().search(
                    [("id", "child_of", order.partner_id.commercial_partner_id.ids)])
                if partner_id not in shippings.mapped('id') and partner_id != order.partner_id.id:
                    return Forbidden()
                Partner.browse(partner_id).sudo().write(checkout)
        return partner_id

    # def checkout_redirection(self, order):
    #     # must have a draft sales order with lines at this point, otherwise reset
    #     if not order or order.state != 'draft':
    #         request.session['sale_order_id'] = None
    #         request.session['sale_transaction_id'] = None
    #         return request.redirect('/shop')
    #
    #     if order and not order.order_line:
    #         return request.redirect('/shop/cart')
    #
    #     # if transaction pending / done: redirect to confirmation
    #     tx = request.env.context.get('website_sale_transaction')
    #     if tx and tx.state != 'draft':
    #         return request.redirect('/shop/payment/confirmation/%s' % order.id)

    @http.route(['/shop/address'], type='http', methods=['GET', 'POST'], auth="public", website=True, sitemap=False)
    def address(self, **kw):
        Partner = request.env['res.partner'].with_context(show_address=1).sudo()
        order = request.website.sale_get_order()
        checked_list = request.website.get_checked_sale_order_line(order.website_order_line)

        if len(checked_list) <= 0:
            return request.redirect('/shop')

        redirection = Website_Sale.checkout_redirection(Website_Sale, order)
        if redirection:
            return redirection

        mode = (False, False)
        can_edit_vat = False
        def_country_id = order.partner_id.country_id
        values, errors = {}, {}

        partner_id = int(kw.get('partner_id', -1))

        # IF PUBLIC ORDER
        if order.partner_id.id == request.website.user_id.sudo().partner_id.id \
                or request.env.user.id == request.website.user_id.sudo().partner_id.id:
            mode = ('new', 'billing')
            can_edit_vat = True
            country_code = request.session['geoip'].get('country_code')
            if country_code:
                def_country_id = request.env['res.country'].search([('code', '=', country_code)], limit=1)
            else:
                def_country_id = request.website.user_id.sudo().country_id
        # IF ORDER LINKED TO A PARTNER
        else:
            if partner_id > 0:
                if partner_id == order.partner_id.id:
                    mode = ('edit', 'billing')
                    can_edit_vat = order.partner_id.can_edit_vat()
                else:
                    shippings = Partner.search([('id', 'child_of', order.partner_id.commercial_partner_id.ids)])
                    if partner_id in shippings.mapped('id'):
                        mode = ('edit', 'shipping')
                    else:
                        return Forbidden()
                if mode:
                    values = Partner.browse(partner_id)
            elif partner_id == -1:
                mode = ('new', 'shipping')
            else:  # no mode - refresh without post?
                return request.redirect('/shop/checkout')

        # IF POSTED
        if 'submitted' in kw:
            pre_values = Website_Sale.values_preprocess(Website_Sale, order, mode, kw)
            errors, error_msg = self.checkout_form_validate(mode, kw, pre_values)
            post, errors, error_msg = Website_Sale.values_postprocess(Website_Sale, order, mode, pre_values, errors, error_msg)

            if errors:
                errors['error_message'] = error_msg
                values = kw
            else:
                partner_id = self._checkout_form_save(mode, post, kw)
                if mode[1] == 'billing':
                    order.partner_id = partner_id
                    order.with_context(not_self_saleperson=True).onchange_partner_id()
                    # This is the *only* thing that the front end user will see/edit anyway when choosing billing address
                    order.partner_invoice_id = partner_id
                    if not kw.get('use_same'):
                        kw['callback'] = kw.get('callback') or \
                                         (not order.only_services and (
                                                     mode[0] == 'edit' and '/shop/checkout' or '/shop/address'))
                elif mode[1] == 'shipping':
                    order.partner_shipping_id = partner_id

                order.message_partner_ids = [(4, partner_id), (3, request.website.partner_id.id)]
                if not errors:
                    return request.redirect(kw.get('callback') or '/shop/confirm_order')

        email_or_phone = 'email' in values and values['email']
        phone_no = 'phone' in values and values['phone']

        if not email_or_phone:
            email = ""
            phone = ""
        else:
            email = str(email_or_phone)
            if email.isdecimal():
                email = ""
                phone = email_or_phone
            else:
                if not phone_no:
                    phone = ""
                else:
                    phone = str(phone_no)

        country = 'country_id' in values and values['country_id'] != '' and request.env['res.country'].browse(
            int(values['country_id']))
        country = country and country.exists() or def_country_id
        render_values = {
            'website_sale_order': order,
            'partner_id': partner_id,
            'mode': mode,
            'checkout': values,
            'can_edit_vat': can_edit_vat,
            'country': country,
            'countries': country.get_website_sale_countries(mode=mode[1]),
            "states": country.get_website_sale_states(mode=mode[1]),
            'error': errors,
            'callback': kw.get('callback'),
            'only_services': order and order.only_services,
            'email': email,
            'phone': phone
        }
        return request.render("website_sale.address", render_values)



class WebsiteSale (WebsiteSale):
    @http.route(['/home'], type='http', auth='public', website=True)
    def home(self, **kw):
        feeling = request.env['feeling.products'].search([('website_published', '=', 'True')])
        
        values = {
            'feeling': feeling,
            'daily_deals': request.env['website.deals'].sudo().get_valid_deals(),
            'homepage_deals': request.env['website.deals'].sudo().get_homepage_deals(),
        }
        return request.render('customizations_by_livep.homepage', values)


    @http.route([
        # '''/shop''',
        # '''/shop/page/<int:page>''',
        # '''/shop/category/<model("product.public.category"):category>''',
        # '''/shop/category/<model("product.public.category"):category>/page/<int:page>''',
        '''/shop/feeling/<model("feeling.products"):feeling>''',
        '''/shop/feeling/<model("feeling.products"):feeling>/page/<int:page>'''
    ], type='http', auth="public", website=True)

    def feelingShop(self, feeling=None, page=0, category=None, search='', ppg=False, **post):
        # if feeling is None:
        #     return super(WebsiteSale, self).shop(**post)
        add_qty = int(post.get('add_qty', 1))
        cat_domain = []
        categ_ids = request.env['feeling.products'].search([('id', '=', int(feeling))]).feeling_product_categories
        for cat in categ_ids:
            cat_domain.append(int(cat))

        Category = request.env['product.public.category']
        if category:
            category = Category.search([('id', '=', int(category))], limit=1)
            if not category or not category.can_access_from_current_website():
                raise NotFound()
        else:
            category = Category

        if ppg:
            try:
                ppg = int(ppg)
                post['ppg'] = ppg
            except ValueError:
                ppg = False
        if not ppg:
            ppg = request.env['website'].get_current_website().shop_ppg or 20

        ppr = request.env['website'].get_current_website().shop_ppr or 4

        attrib_list = request.httprequest.args.getlist('attrib')
        attrib_values = [[int(x) for x in v.split("-")] for v in attrib_list if v]
        attributes_ids = {v[0] for v in attrib_values}
        attrib_set = {v[1] for v in attrib_values}

        domain = WebsiteSale._get_search_domain(WebsiteSale, search, category, attrib_values)

        keep = QueryURL('/shop', category=category and int(category), search=search, attrib=attrib_list,
                        order=post.get('order'))

        pricelist_context, pricelist = WebsiteSale._get_pricelist_context(WebsiteSale)

        request.context = dict(request.context, pricelist=pricelist.id, partner=request.env.user.partner_id)

        url = "/shop"
        if search:
            post["search"] = search
        if attrib_list:
            post['attrib'] = attrib_list

        # Product = request.env['product.template'].search([('sale_ok', '=', True)])

        Product = request.env['product.template'].search([('public_categ_ids', 'in', cat_domain),
                                                          ('sale_ok', '=', True), ('website_published', '=', True)])

        search_product = Product.search([('public_categ_ids','in', cat_domain), ('sale_ok', '=', True), ('website_published', '=', True)],
                                        order=WebsiteSale._get_search_order(WebsiteSale, post))
        website_domain = request.website.website_domain()
        categs_domain = [('parent_id', '=', False)] + website_domain
        if search:
            search_categories = Category.search(
                [('product_tmpl_ids', 'in', search_product.ids)] + website_domain).parents_and_self
            categs_domain.append(('id', 'in', search_categories.ids))
        else:
            search_categories = Category
        categs = Category.search(categs_domain)

        if feeling:
            url = "/shop/feeling/%s" % slug(feeling)

        product_count = len(search_product)
        pager = request.website.pager(url=url, total=product_count, page=page, step=ppg, scope=7, url_args=post)
        offset = pager['offset']
        products = search_product[offset: offset + ppg]

        ProductAttribute = request.env['product.attribute']
        if products:
            # get all products without limit
            attributes = ProductAttribute.search([('product_tmpl_ids', 'in', search_product.ids)])
        else:
            attributes = ProductAttribute.browse(attributes_ids)

        layout_mode = request.session.get('website_sale_shop_layout_mode')
        if not layout_mode:
            if request.website.viewref('website_sale.products_list_view').active:
                layout_mode = 'list'
            else:
                layout_mode = 'grid'

        values = {
            'search': search,
            'category': category,
            'attrib_values': attrib_values,
            'attrib_set': attrib_set,
            'pager': pager,
            'pricelist': pricelist,
            'add_qty': add_qty,
            'products': products,
            'search_count': product_count,  # common for all searchbox
            'bins': TableCompute().process(products, ppg, ppr),
            'ppg': ppg,
            'ppr': ppr,
            'categories': categs,
            'attributes': attributes,
            'keep': keep,
            'search_categories_ids': search_categories.ids,
            'layout_mode': layout_mode,
            'feeling': feeling,
        }
        if category:
            values['main_object'] = category
        if values.get("pager").get('page_end').get('num') < page:
            return "none"
        elif post.get("test"):
            view = request.render("theme_xtremo.wk_lazy_list_product_item", values)
            return view
        else:
            return request.render("website_sale.products", values)

    @http.route([
        '''/shop''',
        '''/shop/page/<int:page>''',
        '''/shop/category/<model("product.public.category"):category>''',
        '''/shop/category/<model("product.public.category"):category>/page/<int:page>'''
    ], type='http', auth="public", website=True)
    def shop(self, page=0, category=None, search='', ppg=False, **post):
        add_qty = int(post.get('add_qty', 1))
        Category = request.env['product.public.category']
        if category:
            category = Category.search([('id', '=', int(category))], limit=1)
            if not category or not category.can_access_from_current_website():
                raise NotFound()
        else:
            category = Category

        if ppg:
            try:
                ppg = int(ppg)
                post['ppg'] = ppg
            except ValueError:
                ppg = False
        if not ppg:
            ppg = request.env['website'].get_current_website().shop_ppg or 20

        ppr = request.env['website'].get_current_website().shop_ppr or 4

        attrib_list = request.httprequest.args.getlist('attrib')
        attrib_values = [[int(x) for x in v.split("-")] for v in attrib_list if v]
        attributes_ids = {v[0] for v in attrib_values}
        attrib_set = {v[1] for v in attrib_values}

        domain = self._get_search_domain(search, category, attrib_values)
        domain.append(('website_published', '=', True))
        domain.append(('is_service', '=', False))
        domain.append(('type', '!=', 'service'))
        keep = QueryURL('/shop', category=category and int(category), search=search, attrib=attrib_list, order=post.get('order'))

        pricelist_context, pricelist = self._get_pricelist_context()

        request.context = dict(request.context, pricelist=pricelist.id, partner=request.env.user.partner_id)

        url = "/shop"
        if search:
            post["search"] = search
        if attrib_list:
            post['attrib'] = attrib_list

        Product = request.env['product.template'].with_context(bin_size=True)




        search_product = Product.search(domain, order=self._get_search_order(post))
        website_domain = request.website.website_domain()
        categs_domain = [('parent_id', '=', False)] + website_domain
        if search:
            search_categories = Category.search([('product_tmpl_ids', 'in', search_product.ids)] + website_domain).parents_and_self
            categs_domain.append(('id', 'in', search_categories.ids))
        else:
            search_categories = Category
        categs = Category.search(categs_domain)

        if category:
            url = "/shop/category/%s" % slug(category)

        product_count = len(search_product)
        pager = request.website.pager(url=url, total=product_count, page=page, step=ppg, scope=7, url_args=post)
        offset = pager['offset']

        if not post:
            products = random.sample(search_product, len(search_product))[offset: offset + ppg]
        else:    
            products = search_product[offset: offset + ppg]

        ProductAttribute = request.env['product.attribute']
        if products:
            # get all products without limit
            attributes = ProductAttribute.search([('product_tmpl_ids', 'in', search_product.ids)])
        else:
            attributes = ProductAttribute.browse(attributes_ids)

        layout_mode = request.session.get('website_sale_shop_layout_mode')
        if not layout_mode:
            if request.website.viewref('website_sale.products_list_view').active:
                layout_mode = 'list'
            else:
                layout_mode = 'grid'

        values = {
            'search': search,
            'category': category,
            'attrib_values': attrib_values,
            'attrib_set': attrib_set,
            'pager': pager,
            'pricelist': pricelist,
            'add_qty': add_qty,
            'products': products,
            'search_count': product_count,  # common for all searchbox
            'bins': TableCompute().process(products, ppg, ppr),
            'ppg': ppg,
            'ppr': ppr,
            'categories': categs,
            'attributes': attributes,
            'keep': keep,
            'search_categories_ids': search_categories.ids,
            'layout_mode': layout_mode,
        }
        if category:
            values['main_object'] = category
        return request.render("website_sale.products", values)

    @http.route([
        '''/service''',
        '''/service/page/<int:page>''',
        '''/service/category/<model("product.public.category"):category>''',
        '''/service/category/<model("product.public.category"):category>/page/<int:page>'''
    ], type='http', auth="public", website=True)
    def service(self, page=0, category=None, search='', ppg=False, **post):
        add_qty = int(post.get('add_qty', 1))
        Category = request.env['product.public.category']
        if category:
            category = Category.search([('id', '=', int(category))], limit=1)
            if not category or not category.can_access_from_current_website():
                raise NotFound()
        else:
            category = Category

        if ppg:
            try:
                ppg = int(ppg)
                post['ppg'] = ppg
            except ValueError:
                ppg = False
        if not ppg:
            ppg = request.env['website'].get_current_website().shop_ppg or 20

        ppr = request.env['website'].get_current_website().shop_ppr or 4

        attrib_list = request.httprequest.args.getlist('attrib')
        attrib_values = [[int(x) for x in v.split("-")] for v in attrib_list if v]
        attributes_ids = {v[0] for v in attrib_values}
        attrib_set = {v[1] for v in attrib_values}

        domain = self._get_search_domain(search, category, attrib_values)
        domain.append(('website_published', '=', True))
        keep = QueryURL('/service', category=category and int(category), search=search, attrib=attrib_list,
                        order=post.get('order'))

        print("Keep", keep)
        print(keep.__dict__)

        pricelist_context, pricelist = self._get_pricelist_context()

        request.context = dict(request.context, pricelist=pricelist.id, partner=request.env.user.partner_id)

        url = "/service"
        if search:
            post["search"] = search
        if attrib_list:
            post['attrib'] = attrib_list

        Product = request.env['product.template'].with_context(bin_size=True)

        # bk_products = Product.search([('is_booking_type', '=', True)])
        # for pobj in bk_products:
        #     print("Booking Products", bk_products)
        #     if pobj.br_end_date < fields.Date.today():
        #         pobj.website_published = False
        #     else:
        #         pobj.website_published = True
        #
        # for pobj in bk_products:
        #     print(pobj.website_published)

        ticket_domain = domain + [('is_service', '=', True)]
        ticket_product = Product.search(ticket_domain, order=self._get_search_order(post))

        booking_domain = domain + [('is_booking_type', '=', True)]
        booking_product = Product.search(booking_domain, order=self._get_search_order(post))

        booking_active_domain = domain + [('br_end_date', '>=', fields.Date.today()), ('website_published', '=', True)]
        booking_product_active = booking_product.search(booking_active_domain, order=self._get_search_order(post))

        # Service and Booking Products Price Accurate Sorting
        sort_product = booking_product_active + ticket_product
        product_prices = []
        for price in range(len(sort_product)):
            if sort_product[price].is_service:
                product_prices.append(sort_product[price].list_price)
            elif sort_product[price].is_booking_type:
                product_prices.append(sort_product[price].get_booking_onwards_price())

        list_product = [x for _,x in sorted(zip(product_prices, sort_product))]
        sort_data = {key:value for value,key in enumerate(list_product)}

        # Servce and Booking Products Sorting
        if 'list_price asc' in post.values():
            search_product = sort_product.sorted(key=sort_data.get)
        elif 'list_price desc' in post.values():
            search_product = sort_product.sorted(key=sort_data.get, reverse=True)
        elif 'name asc' in post.values():
            search_product = sort_product.sorted('name')
        elif 'name desc' in post.values():
            search_product = sort_product.sorted('name', reverse=True)
        else:
            search_product = sort_product

        website_domain = request.website.website_domain()
        categs_domain = [('parent_id', '=', False)] + website_domain
        if search:
            search_categories = Category.search(
                [('product_tmpl_ids', 'in', search_product.ids)] + website_domain).parents_and_self
            categs_domain.append(('id', 'in', search_categories.ids))
        else:
            search_categories = Category
        categs = Category.search(categs_domain)

        if category:
            url = "/service/category/%s" % slug(category)

        product_count = len(search_product)
        pager = request.website.pager(url=url, total=product_count, page=page, step=ppg, scope=7, url_args=post)
        offset = pager['offset']

        if not post:
            products = random.sample(search_product, len(search_product))[offset: offset + ppg]
        else:    
            products = search_product[offset: offset + ppg]

        ProductAttribute = request.env['product.attribute']
        if products:
            # get all products without limit
            attributes = ProductAttribute.search([('product_tmpl_ids', 'in', search_product.ids)])
        else:
            attributes = ProductAttribute.browse(attributes_ids)

        layout_mode = request.session.get('website_sale_shop_layout_mode')
        if not layout_mode:
            if request.website.viewref('website_sale.products_list_view').active:
                layout_mode = 'list'
            else:
                layout_mode = 'grid'

        values = {
            'search': search,
            'category': category,
            'attrib_values': attrib_values,
            'attrib_set': attrib_set,
            'pager': pager,
            'pricelist': pricelist,
            'add_qty': add_qty,
            'products': products,
            'search_count': product_count,  # common for all searchbox
            'bins': TableCompute().process(products, ppg, ppr),
            'ppg': ppg,
            'ppr': ppr,
            'categories': categs,
            'attributes': attributes,
            'keep': keep,
            'search_categories_ids': search_categories.ids,
            'layout_mode': layout_mode,
        }
        if category:
            values['main_object'] = category

        if values.get("pager").get('page_end').get('num') < page:
            return "none"
        elif post.get("test"):
            view = request.render("theme_xtremo.wk_lazy_list_product_item", values)
            return view
        else:
            return request.render("website_sale.products", values)

    @http.route(['/shop/product/<model("product.template"):product>', '/service/<model("product.template"):product>'],
                type='http', auth="public", website=True)
    def product(self, product, category='', search='', **kwargs):
        if not product.can_access_from_current_website():
            raise NotFound()

        return request.render("website_sale.product", self._prepare_product_values(product, category, search, **kwargs))

    @http.route(['/voucher_valid_product'], type='json', auth='public', website=True)
    def voucher_valid_product(self):
        order = request.website.sale_get_order()
        checked_list = request.website.get_checked_sale_order_line(order.website_order_line)

        voucher_valid = True
        for line in order.order_line:
            print(line)
            # if line.is_voucher:
            #     voucher = line.wk_voucher_id
            #     voucher_code = voucher.voucher_code
            #     print(voucher_code)
            #     applied_products = voucher.product_ids
            #     print(applied_products)
            #
            #     if applied_products:
            #         voucher_valid = False
            #         for sol in checked_list:
            #             if sol.product_template_id in applied_products:
            #                 voucher_valid = True

            if line.is_voucher:
                voucher = line.wk_voucher_id
                voucher_valid = False

                for sol in checked_list:
                    if (sol.product_id.marketplace_seller_id == voucher.marketplace_seller_id)  and len(checked_list) > 1:
                        voucher_valid = True


        return {
            "voucher_valid_product": voucher_valid
        }






    @http.route(['/shop/checkout'], type='http', auth='public', website=True)
    def checkout(self, **post):
        order = request.website.sale_get_order()
        print("Checkout Order", order)
        # for line in order.order_line:
        #     print(line)
        #     if line.is_voucher:
        #         voucher = line.wk_voucher_id
        #         voucher_code = voucher.voucher_code
        #         print(voucher_code)
        #         applied_products = voucher.product_ids
        #         print(applied_products)

        checked_list = request.website.get_checked_sale_order_line(order.website_order_line)
        # print(checked_list)
        # if applied_products:
        #     voucher_valid = False
        #     for sol in checked_list:
        #         if sol.product_template_id in applied_products:
        #             voucher_valid = True

        # print('Voucher Valid', voucher_valid)

        if len(checked_list) <= 0:
            return request.redirect('/shop')

        return super(WebsiteSale, self).checkout(**post)

    @http.route(['/shop/checkout/select/products'], type='json', auth='public', website=True)
    def selectProduct(self, orderLineId):
        order = request.website.sale_get_order()

        orderLine = order.website_order_line.search([('id', '=', orderLineId)])

        for o in order.website_order_line:
            if o.id == orderLineId:
                if orderLine.selected_checkout == False:
                    orderLine.update({'selected_checkout': True})
                    order.update({
                        'checked_amount_untaxed': order.checked_amount_untaxed,
                        'checked_amount_tax': order.checked_amount_tax,
                        'checked_amount_total': order.checked_amount_untaxed + order.checked_amount_tax,
                    })
                else:
                    orderLine.update({'selected_checkout': False})
                    order.update({
                        'checked_amount_untaxed': order.checked_amount_untaxed,
                        'checked_amount_tax': order.checked_amount_tax,
                        'checked_amount_total': order.checked_amount_untaxed + order.checked_amount_tax,
                    })
        # checked_list = request.website.get_checked_sale_order_line(order.website_order_line)

    @http.route(['/shop/cart'], type='http', auth="public", website=True, sitemap=False)
    def cart(self, access_token=None, revive='', **post):
        result = super(WebsiteSale, self).cart(**post)

        order = request.website.sale_get_order()
        checked_list = request.website.get_checked_sale_order_line(order.website_order_line)
        order_id_list = request.website.get_sale_order_id_list()

        if request.env.user.id == request.website.user_id.sudo().partner_id.id:
            guest = True
        else:
            guest = False

        result.qcontext.update({
            'cart_sale_order': checked_list,
            'order_id_list': order_id_list,
            'guest': guest,
        })

        return result

    # To show only checked products on /shop/payment page
    @http.route(['/shop/payment'], type='http', auth="public", website=True, sitemap=False)
    def payment(self, **post):

        result = super(WebsiteSale, self).payment(**post)

        order = request.website.sale_get_order()
        checked_list = request.website.get_checked_sale_order_line(order.website_order_line)
        order_id_list = request.website.get_sale_order_id_list()

        result.qcontext.update({
            'cart_sale_order': checked_list,
            'order_id_list': order_id_list,
        })
        return result


class Website(Website):

    @http.route(website=True, auth="public", sitemap=False)
    def web_login(self, redirect=None, *args, **kw):
        response = super(Website, self).web_login(
            redirect=redirect, *args, **kw)
        if not redirect and request.params['login_success']:
            redirect = '/shop'
            return http.redirect_with_hash(redirect)
        return response

    @http.route(['/shop/confirmation'], type='http', auth="public", website=True, sitemap=False)
    def payment_confirmation(self, **post):
        """ End of checkout process controller. Confirmation is basically seing
        the status of a sale.order. State at this point :

         - should not have any context / session info: clean them
         - take a sale.order id, because we request a sale.order and are not
           session dependant anymore
        """
        sale_order_id = request.session.get('sale_last_order_id')
        if sale_order_id:
            order = request.env['sale.order'].sudo().browse(sale_order_id)
            if order and order.state in ('sale','approve_by_admin'):
                newlp_sale_order_id = request.session.get('newlp_sale_order_id')
                newlp_website_sale_current_pl = request.session.get('newlp_website_sale_current_pl')
                request.env['website'].sale_replace(newlp_sale_order_id, newlp_website_sale_current_pl)

            return request.render("website_sale.confirmation", {'order': order})
        else:
            return request.redirect('/shop')

class WebsiteSaleWishlist(WebsiteSale):

    @http.route(['/shop/wishlist/add'], type='json', auth="public", website=True)
    def add_to_wishlist(self, product_id, price=False, **kw):
        if not price:
            pricelist_context, pl = self._get_pricelist_context()
            p = request.env['product.product'].with_context(pricelist_context, display_default_code=False).browse(product_id)
            price = p._get_combination_info_variant()['price']

        Wishlist = request.env['product.wishlist']
        if request.website.is_public_user():
            Wishlist = Wishlist.sudo()
            partner_id = False
        else:
            partner_id = request.env.user.partner_id.id

        wish_id = Wishlist._add_to_wishlist(
            pl.id,
            pl.currency_id.id,
            request.website.id,
            price,
            product_id,
            partner_id
        )

        # if not partner_id:
        #     request.session['wishlist_ids'] = request.session.get('wishlist_ids', []) + [wish_id.id]

        return wish_id
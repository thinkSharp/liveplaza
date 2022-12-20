# -*- coding: utf-8 -*-
#################################################################################
##    Copyright (c) 2019-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>)
#    You should have received a copy of the License along with this program.
#    If not, see <https://store.webkul.com/license.html/>
#################################################################################

from odoo import api, fields, models, tools, _
from odoo.exceptions import UserError, ValidationError
from odoo.tools import float_repr
from odoo.tools.misc import get_lang
from datetime import datetime, timedelta, date
from dateutil.relativedelta import relativedelta
import json
from itertools import chain

class DealsPriceListStyle(models.Model):
    _name = "deals.pricelist.style"
    _description = "Deals Pricelist Style"

    name = fields.Char(string='Style Name', required=True)
    html_class = fields.Char(string='HTML Classes')

class ProductPricelist(models.Model):
    _inherit = "product.pricelist"

    def unlink(self):
        if self.name == "Deals Dummy Pricelist":
            raise UserError('This Pricelist Can Not be deleted as this is used by website daily deals Module.')
        else:
            return super(ProductPricelist, self).unlink();

    def _compute_price_rule_get_items(self, products_qty_partner, date, uom_id, prod_tmpl_ids, prod_ids, categ_ids):
        self.ensure_one()
        # Load all rules
        self.env['product.pricelist.item'].flush(['price', 'currency_id', 'company_id'])
        self.env.cr.execute(
            """
            SELECT
                item.id
            FROM
                product_pricelist_item AS item
            LEFT JOIN product_category AS categ ON item.categ_id = categ.id
            WHERE
                (item.product_tmpl_id IS NULL OR item.product_tmpl_id = any(%s))
                AND (item.product_id IS NULL OR item.product_id = any(%s))
                AND (item.categ_id IS NULL OR item.categ_id = any(%s))
                AND (item.pricelist_id = %s)
                AND (item.date_start IS NULL OR item.date_start<=%s)
                AND (item.date_end IS NULL OR item.date_end>=%s)
            ORDER BY
                item.applied_on, item.min_quantity desc, categ.complete_name desc, item.id desc
            """,
            (prod_tmpl_ids, prod_ids, categ_ids, self.id, date, date))
        # NOTE: if you change `order by` on that query, make sure it matches
        # _order from model to avoid inconstencies and undeterministic issues.

        item_ids = [x[0] for x in self.env.cr.fetchall()]
        return self.env['product.pricelist.item'].browse(item_ids)

    def _compute_price_rule_get_items_booking(self, products_qty_partner, date, uom_id, prod_tmpl_ids, prod_ids, categ_ids):
        self.ensure_one()
        # Load all rules
        self.env['product.pricelist.item'].flush(['price', 'currency_id', 'company_id'])
        self.env.cr.execute(
            """
            SELECT
                item.id
            FROM
                product_pricelist_item AS item
            LEFT JOIN product_category AS categ ON item.categ_id = categ.id
            WHERE
                (item.product_tmpl_id IS NULL OR item.product_tmpl_id = any(%s))
                AND (item.product_id IS NULL OR item.product_id = any(%s))
                AND (item.categ_id IS NULL OR item.categ_id = any(%s))
                AND (item.pricelist_id = %s)
                AND (item.date_start IS NULL OR item.date_start<=%s)
                AND (item.date_end IS NULL OR item.date_end>=%s)
            ORDER BY
                item.applied_on, item.min_quantity desc, categ.complete_name desc, item.id desc
            """,
            (prod_tmpl_ids, prod_ids, categ_ids, self.id, date, date))
        # NOTE: if you change `order by` on that query, make sure it matches
        # _order from model to avoid inconstencies and undeterministic issues.

        item_ids = [x[0] for x in self.env.cr.fetchall()]
        return self.env['product.pricelist.item'].browse(item_ids)

    def _compute_price_rule(self, products_qty_partner, date=False, uom_id=False):
        """ Low-level method - Mono pricelist, multi products
        Returns: dict{product_id: (price, suitable_rule) for the given pricelist}

        Date in context can be a date, datetime, ...

            :param products_qty_partner: list of typles products, quantity, partner
            :param datetime date: validity date
            :param ID uom_id: intermediate unit of measure
        """
        self.ensure_one()
        if not date:
            date = self._context.get('date') or fields.Date.today()
        date = fields.Date.to_date(date)  # boundary conditions differ if we have a datetime
        if not uom_id and self._context.get('uom'):
            uom_id = self._context['uom']
        if uom_id:
            # rebrowse with uom if given
            products = [item[0].with_context(uom=uom_id) for item in products_qty_partner]
            products_qty_partner = [(products[index], data_struct[1], data_struct[2]) for index, data_struct in enumerate(products_qty_partner)]
        else:
            products = [item[0] for item in products_qty_partner]

        if not products:
            return {}

        categ_ids = {}
        for p in products:
            categ = p.categ_id
            while categ:
                categ_ids[categ.id] = True
                categ = categ.parent_id
        categ_ids = list(categ_ids)

        is_product_template = products[0]._name == "product.template"
        if is_product_template:
            prod_tmpl_ids = [tmpl.id for tmpl in products]
            # all variants of all products
            prod_ids = [p.id for p in
                        list(chain.from_iterable([t.product_variant_ids for t in products]))]
        else:
            prod_ids = [product.id for product in products]
            prod_tmpl_ids = [product.product_tmpl_id.id for product in products]

        items = self._compute_price_rule_get_items(products_qty_partner, date, uom_id, prod_tmpl_ids, prod_ids, categ_ids)

        results = {}
        for product, qty, partner in products_qty_partner:
            results[product.id] = 0.0
            suitable_rule = False

            # Final unit price is computed according to `qty` in the `qty_uom_id` UoM.
            # An intermediary unit price may be computed according to a different UoM, in
            # which case the price_uom_id contains that UoM.
            # The final price will be converted to match `qty_uom_id`.
            qty_uom_id = self._context.get('uom') or product.uom_id.id
            price_uom_id = product.uom_id.id
            qty_in_product_uom = qty
            if qty_uom_id != product.uom_id.id:
                try:
                    qty_in_product_uom = self.env['uom.uom'].browse([self._context['uom']])._compute_quantity(qty, product.uom_id)
                except UserError:
                    # Ignored - incompatible UoM in context, use default product UoM
                    pass

            # if Public user try to access standard price from website sale, need to call price_compute.
            # TDE SURPRISE: product can actually be a template
            #price = product.price_compute('list_price')[product.id]
            if product.is_booking_type:
                if is_product_template:
                    price = product.get_booking_onwards_price_pl()
                else:
                    price = product.product_tmpl_id.get_booking_onwards_price_pl()
            else:
                price = product.price_compute('list_price')[product.id]

            price_uom = self.env['uom.uom'].browse([qty_uom_id])
            for rule in items:
                if rule.min_quantity and qty_in_product_uom < rule.min_quantity:
                    continue
                if is_product_template:
                    if rule.product_tmpl_id and product.id != rule.product_tmpl_id.id:
                        continue
                    if rule.product_id and not (product.product_variant_count == 1 and product.product_variant_id.id == rule.product_id.id):
                        # product rule acceptable on template if has only one variant
                        continue
                    if rule.isMulti_products and rule.product_tmpl_ids:
                        if product not in rule.product_tmpl_ids:
                            continue
                    if rule.isMulti_variants and rule.product_ids:
                        if product.product_variant_id not in rule.product_ids:
                            continue
                else:
                    if rule.product_tmpl_id and product.product_tmpl_id.id != rule.product_tmpl_id.id:
                        continue
                    if rule.product_id and product.id != rule.product_id.id:
                        continue
                    if rule.isMulti_products and rule.product_tmpl_ids:
                        if product.product_tmpl_id not in rule.product_tmpl_ids:
                            continue
                    if rule.isMulti_variants and rule.product_ids:
                        if product.product_variant_id not in rule.product_ids:
                            continue

                if rule.categ_id:
                    cat = product.categ_id
                    while cat:
                        if cat.id == rule.categ_id.id:
                            break
                        cat = cat.parent_id
                    if not cat:
                        continue

                if rule.base == 'pricelist' and rule.base_pricelist_id:
                    if product.is_booking_type:
                        if is_product_template:
                            price = product.get_booking_onwards_price_pl()
                        else:
                            price = product.product_tmpl_id.get_booking_onwards_price_pl()
                    else:
                        price_tmp = rule.base_pricelist_id._compute_price_rule([(product, qty, partner)], date, uom_id)[product.id][0]  # TDE: 0 = price, 1 = rule
                        price = rule.base_pricelist_id.currency_id._convert(price_tmp, self.currency_id, self.env.company, date, round=False)
                else:
                    # if base option is public price take sale price else cost price of product
                    # price_compute returns the price in the context UoM, i.e. qty_uom_id
                    if product.is_booking_type:
                        if is_product_template:
                            price = product.get_booking_onwards_price()
                        else:
                            price = product.product_tmpl_id.get_booking_onwards_price()
                    else:
                        price = product.price_compute(rule.base)[product.id]

                convert_to_price_uom = (lambda price: product.uom_id._compute_price(price, price_uom))

                if price is not False:
                    if rule.compute_price == 'fixed':
                        price = convert_to_price_uom(rule.fixed_price)
                    elif rule.compute_price == 'fixed_discount':
                        price = (price - convert_to_price_uom(rule.fixed_discount))
                    elif rule.compute_price == 'percentage':
                        price = (price - (price * (rule.percent_price / 100))) or 0.0
                    else:
                        # complete formula
                        price_limit = price
                        price = (price - (price * (rule.price_discount / 100))) or 0.0
                        if rule.price_round:
                            price = tools.float_round(price, precision_rounding=rule.price_round)

                        if rule.price_surcharge:
                            price_surcharge = convert_to_price_uom(rule.price_surcharge)
                            price += price_surcharge

                        if rule.price_min_margin:
                            price_min_margin = convert_to_price_uom(rule.price_min_margin)
                            price = max(price, price_limit + price_min_margin)

                        if rule.price_max_margin:
                            price_max_margin = convert_to_price_uom(rule.price_max_margin)
                            price = min(price, price_limit + price_max_margin)
                    suitable_rule = rule
                break
            # Final price conversion into pricelist currency
            if suitable_rule and suitable_rule.compute_price != 'fixed' and suitable_rule.base != 'pricelist':
                if suitable_rule.base == 'standard_price':
                    cur = product.cost_currency_id
                else:
                    cur = product.currency_id
                price = cur._convert(price, self.currency_id, self.env.company, date, round=False)

            if not suitable_rule:
                cur = product.currency_id
                price = cur._convert(price, self.currency_id, self.env.company, date, round=False)

            results[product.id] = (price, suitable_rule and suitable_rule.id or False)

        return results

    def _compute_price_rule_booking(self, products_qty_partner, dplan_id, dplan_price, date=False, uom_id=False):
        """ Low-level method - Mono pricelist, multi products
        Returns: dict{product_id: (price, suitable_rule) for the given pricelist}

        Date in context can be a date, datetime, ...

            :param products_qty_partner: list of typles products, quantity, partner
            :param datetime date: validity date
            :param ID uom_id: intermediate unit of measure
        """
        self.ensure_one()
        if not date:
            date = self._context.get('date') or fields.Date.today()
        date = fields.Date.to_date(date)  # boundary conditions differ if we have a datetime
        if not uom_id and self._context.get('uom'):
            uom_id = self._context['uom']
        if uom_id:
            # rebrowse with uom if given
            products = [item[0].with_context(uom=uom_id) for item in products_qty_partner]
            products_qty_partner = [(products[index], data_struct[1], data_struct[2]) for index, data_struct in enumerate(products_qty_partner)]
        else:
            products = [item[0] for item in products_qty_partner]

        if not products:
            return {}

        categ_ids = {}
        for p in products:
            categ = p.categ_id
            while categ:
                categ_ids[categ.id] = True
                categ = categ.parent_id
        categ_ids = list(categ_ids)

        is_product_template = products[0]._name == "product.template"
        if is_product_template:
            prod_tmpl_ids = [tmpl.id for tmpl in products]
            # all variants of all products
            prod_ids = [p.id for p in
                        list(chain.from_iterable([t.product_variant_ids for t in products]))]
        else:
            prod_ids = [product.id for product in products]
            prod_tmpl_ids = [product.product_tmpl_id.id for product in products]

        items = self._compute_price_rule_get_items_booking(products_qty_partner, date, uom_id, prod_tmpl_ids, prod_ids, categ_ids)

        results = {}
        for product, qty, partner in products_qty_partner:
            results[product.id] = 0.0
            suitable_rule = False

            # Final unit price is computed according to `qty` in the `qty_uom_id` UoM.
            # An intermediary unit price may be computed according to a different UoM, in
            # which case the price_uom_id contains that UoM.
            # The final price will be converted to match `qty_uom_id`.
            qty_uom_id = self._context.get('uom') or product.uom_id.id
            price_uom_id = product.uom_id.id
            qty_in_product_uom = qty
            if qty_uom_id != product.uom_id.id:
                try:
                    qty_in_product_uom = self.env['uom.uom'].browse([self._context['uom']])._compute_quantity(qty, product.uom_id)
                except UserError:
                    # Ignored - incompatible UoM in context, use default product UoM
                    pass

            # if Public user try to access standard price from website sale, need to call price_compute.
            # TDE SURPRISE: product can actually be a template
            #if product.id == 798:
            #    print("Hello")
            #if product.is_booking_type == True and product._name != "product.product":
            #    price = product.get_booking_onwards_price_pl()
            #else:
            #    price = product.price_compute('list_price')[product.id]
            price = dplan_price
            price_uom = self.env['uom.uom'].browse([qty_uom_id])
            for rule in items:
                if rule.min_quantity and qty_in_product_uom < rule.min_quantity:
                    continue
                if is_product_template:
                    if rule.product_tmpl_id and product.id != rule.product_tmpl_id.id:
                        continue
                    if rule.product_id and not (product.product_variant_count == 1 and product.product_variant_id.id == rule.product_id.id):
                        # product rule acceptable on template if has only one variant
                        continue
                    if rule.isMulti_products and rule.product_tmpl_ids:
                        if product not in rule.product_tmpl_ids:
                            continue
                    if rule.isMulti_variants and rule.product_ids:
                        if product.product_variant_id not in rule.product_ids:
                            continue
                else:
                    if rule.product_tmpl_id and product.product_tmpl_id.id != rule.product_tmpl_id.id:
                        continue
                    if rule.product_id and product.id != rule.product_id.id:
                        continue
                    if rule.isMulti_products and rule.product_tmpl_ids:
                        if product.product_tmpl_id not in rule.product_tmpl_ids:
                            continue
                    if rule.isMulti_variants and rule.product_ids:
                        if product.product_variant_id not in rule.product_ids:
                            continue

                if rule.categ_id:
                    cat = product.categ_id
                    while cat:
                        if cat.id == rule.categ_id.id:
                            break
                        cat = cat.parent_id
                    if not cat:
                        continue

                # if rule.base == 'pricelist' and rule.base_pricelist_id:
                #     if product.is_booking_type == True and product._name != "product.product":
                #         price = product.get_booking_onwards_price_pl()
                #     else:
                #         price_tmp = rule.base_pricelist_id._compute_price_rule([(product, qty, partner)], date, uom_id)[product.id][0]  # TDE: 0 = price, 1 = rule
                #         price = rule.base_pricelist_id.currency_id._convert(price_tmp, self.currency_id, self.env.company, date, round=False)
                # else:
                #     # if base option is public price take sale price else cost price of product
                #     # price_compute returns the price in the context UoM, i.e. qty_uom_id
                #     price = product.price_compute(rule.base)[product.id]
                #     if product.is_booking_type == True and product._name != "product.product":
                #         price = product.get_booking_onwards_price_pl()
                #     else:
                #         price = product.price_compute(rule.base)[product.id]
                #
                convert_to_price_uom = (lambda price: product.uom_id._compute_price(price, price_uom))

                if price is not False:
                    if rule.compute_price == 'fixed':
                        price = convert_to_price_uom(rule.fixed_price)
                    elif rule.compute_price == 'fixed_discount':
                        price = (price - convert_to_price_uom(rule.fixed_discount))
                    elif rule.compute_price == 'percentage':
                        price = (price - (price * (rule.percent_price / 100))) or 0.0
                    else:
                        # complete formula
                        price_limit = price
                        price = (price - (price * (rule.price_discount / 100))) or 0.0
                        if rule.price_round:
                            price = tools.float_round(price, precision_rounding=rule.price_round)

                        if rule.price_surcharge:
                            price_surcharge = convert_to_price_uom(rule.price_surcharge)
                            price += price_surcharge

                        if rule.price_min_margin:
                            price_min_margin = convert_to_price_uom(rule.price_min_margin)
                            price = max(price, price_limit + price_min_margin)

                        if rule.price_max_margin:
                            price_max_margin = convert_to_price_uom(rule.price_max_margin)
                            price = min(price, price_limit + price_max_margin)
                    suitable_rule = rule
                break
            # Final price conversion into pricelist currency
            if suitable_rule and suitable_rule.compute_price != 'fixed' and suitable_rule.base != 'pricelist':
                if suitable_rule.base == 'standard_price':
                    cur = product.cost_currency_id
                else:
                    cur = product.currency_id
                price = cur._convert(price, self.currency_id, self.env.company, date, round=False)

            if not suitable_rule:
                cur = product.currency_id
                price = cur._convert(price, self.currency_id, self.env.company, date, round=False)

            results[dplan_id] = price

        return results

    @api.model
    def create(self, vals):
        active_pricelists = self.env['product.pricelist'].search([('active', '=', True),('selectable', '=', True)])
        if vals.get('selectable', False):            
            if active_pricelists:
                if len(active_pricelists) > 0:
                    raise UserError('There is a selectable pricelist already and cannot make this pricelist SELECTABLE. Please unchecked the selectable field to continue.')
        else:            
            if not active_pricelists:
                if len(active_pricelists) == 0:
                    raise UserError('At least one pricelist must be selectable.')
        return super(ProductPricelist, self).create(vals)

    def write(self, values):
        active_pricelists = self.env['product.pricelist'].search([('active', '=', True),('selectable', '=', True),('id', '!=', self.id)])
        if values.get('selectable', False):       
            if active_pricelists:
                if values.get('selectable') == True:   
                    if len(active_pricelists) > 0:
                        raise UserError('There is a selectable pricelist already and cannot make this pricelist SELECTABLE. Please unchecked the selectable field to continue.')
            else:
                if values.get('selectable') == False: 
                    raise UserError('At least one pricelist must be selectable.')
        #else:            
        #    if not active_pricelists:
        #        if len(active_pricelists) == 0:
        #            raise UserError('At least one pricelist must be selectable.')        

        res = super(ProductPricelist, self).write(values)
        # When the pricelist changes we need the product.template price
        # to be invalided and recomputed.
        self.flush()
        self.invalidate_cache()
        return res
        

class ProductPricelistItem(models.Model):
    _inherit = "product.pricelist.item"

    website_deals_m2o = fields.Many2one('website.deals', 'Corresponding Deal', help="My Deals", ondelete="cascade")
    actual_price = fields.Float(related='product_tmpl_id.list_price', string='Actual Price', store=True)
    discounted_price = fields.Float('Discounted Price', default=0.0)
    website_size_x = fields.Integer('Size X', default=1)
    website_size_y = fields.Integer('Size Y', default=1)
    website_style_ids = fields.Many2many('deals.pricelist.style', string='Styles')    
    deal_applied_on = fields.Selection([('1_product', 'Product'), ('0_product_variant', 'Product Variant')], "Apply On",
                                       default=False, required=True,
                                       help='Pricelist Item applicable on selected option')
    product_ids = fields.Many2many('product.product', 'products_pricelist_item_rel', 'pricelist_item_id', 'product_product_id',
                                   string='Product Variants', required=True)
    product_tmpl_ids = fields.Many2many('product.template', 'product_tmpl_pricelist_item_rel', 'pricelist_item_id', 'product_tmpl_id',
                                   string='Products', required=True)
    active = fields.Boolean(readonly=True, related="pricelist_id.active", store=True)
    isMulti_variants = fields.Boolean("Multiple Variants", help="It is for Multiple product variants selection.")
    isMulti_products = fields.Boolean("Multiple Products", help="It is for Multiple products selection.")
    isMulti = fields.Boolean("Multiple", help="It is for Multiple products selection.")
    isGenerated = fields.Boolean("Is Generated", default=False, help="It is for Multiple products generated process.")
    group_id = fields.Many2one('product.pricelist.item', 'Group Pricelist Item', index=True, readonly=True, ondelete='cascade')
    compute_price = fields.Selection([
        ('fixed_discount', 'Fixed Discount'),
        ('fixed', 'Fixed Price'),
        ('percentage', 'Percentage (discount)'),
        ('formula', 'Formula')], index=True, default='fixed_discount', required=True)
    fixed_discount = fields.Float('Fixed Discount', digits='Product Price')
    available_product_ids = fields.Many2many("product.template", compute='_compute_available_product', string="Available Products")
    available_variant_ids = fields.Many2many("product.product", compute='_compute_available_variant', string="Available Variants")
    multiproduct_domain = fields.Char(compute="_compute_product_domain", readonly=True, store=False,)
    multivariant_domain = fields.Char(compute="_compute_variant_domain", readonly=True, store=False,)
    
    @api.onchange('deal_applied_on')
    @api.depends('deal_applied_on')
    def onchange_deal_applied_on(self):
        self.applied_on = self.deal_applied_on
        self.pricelist_id = self.website_deals_m2o.deal_pricelist
        self.min_quantity = 1

    @api.depends('applied_on')
    def _compute_available_product(self):
        for rec in self:
            if rec.website_deals_m2o.marketplace_seller_id:
                booking_ids = self.env['product.template'].search([('is_booking_type', '=', True), ('status', '=', 'approved'), 
                                                        ('marketplace_seller_id','=',rec.website_deals_m2o.marketplace_seller_id.id), ('active', '=', True)])
                if booking_ids:
                    rec.available_product_ids += booking_ids
                
                product_ids = self.env['product.template'].search([('virtual_available', '>', 0), ('status', '=', 'approved'), 
                                                        ('marketplace_seller_id','=',rec.website_deals_m2o.marketplace_seller_id.id), ('active', '=', True)])
                if product_ids:
                    rec.available_product_ids += product_ids
            else:
                booking_ids = self.env['product.template'].search([('is_booking_type', '=', True), ('status', '=', 'approved'), ('active', '=', True)])
                if booking_ids:
                    rec.available_product_ids += booking_ids
                
                product_ids = self.env['product.template'].search([('virtual_available', '>', 0), ('status', '=', 'approved'), ('active', '=', True)])
                if product_ids:
                    rec.available_product_ids += product_ids
            
            
    @api.depends('applied_on')
    def _compute_available_variant(self):
        for rec in self:
            if rec.website_deals_m2o.marketplace_seller_id:
                booking_ids = self.env['product.product'].search([('is_booking_type', '=', True), 
                                    ('status', '=', 'approved'), ('marketplace_seller_id','=',rec.website_deals_m2o.marketplace_seller_id.id), ('active', '=', True)])
                if booking_ids:
                    rec.available_variant_ids += booking_ids
                
                variant_ids = self.env['product.product'].search([('virtual_available', '>', 0), 
                                        ('status', '=', 'approved'), ('marketplace_seller_id','=',rec.website_deals_m2o.marketplace_seller_id.id), ('active', '=', True)])
                if variant_ids:
                    rec.available_variant_ids += variant_ids
            else:               
                booking_ids = self.env['product.product'].search([('is_booking_type', '=', True), ('status', '=', 'approved'), ('active', '=', True)])
                if booking_ids:
                    rec.available_variant_ids += booking_ids
                
                variant_ids = self.env['product.product'].search([('virtual_available', '>', 0), ('status', '=', 'approved'), ('active', '=', True)])
                if variant_ids:
                    rec.available_variant_ids += variant_ids            

    @api.depends('applied_on')
    def _compute_product_domain(self):
        for rec in self:
            cpd_list = []
            booking_ids = self.env['product.template'].search([('is_booking_type', '=', True), 
                                ('status', '=', 'approved'), ('marketplace_seller_id','=',rec.website_deals_m2o.marketplace_seller_id.id), ('active', '=', True)])
            if booking_ids:
                for bids in booking_ids:
                    cpd_list.append(bids.id)
            
            product_ids = self.env['product.template'].search([('virtual_available', '>', 0), 
                                ('status', '=', 'approved'), ('marketplace_seller_id','=',rec.website_deals_m2o.marketplace_seller_id.id), ('active', '=', True)])
            if product_ids:
                for pids in product_ids:
                    cpd_list.append(pids.id)
            rec.multiproduct_domain = json.dumps([('id', 'in', cpd_list)] )
                
    @api.depends('applied_on')
    def _compute_variant_domain(self):
        for rec in self:
            cvd_list = []
            booking_ids = self.env['product.product'].search([('is_booking_type', '=', True), 
                                ('status', '=', 'approved'), ('active', '=', True)])
            if booking_ids:
                for bids in booking_ids:
                    cvd_list.append(bids.id)
            
            variant_ids = self.env['product.product'].search([('virtual_available', '>', 0), 
                                ('status', '=', 'approved'), ('active', '=', True)])
            if variant_ids:
                for vids in variant_ids:
                    cvd_list.append(vids.id)
                    
            rec.multivariant_domain = json.dumps([('id', 'in', cvd_list)] )

    @api.constrains('product_id', 'product_tmpl_id', 'categ_id')
    def _check_product_consistency(self):
        for item in self:
            if item.applied_on == "2_product_category" and not item.categ_id:
                raise ValidationError(_("Please specify the category for which this rule should be applied"))
            elif item.applied_on == "1_product" and not (item.product_tmpl_id or item.product_tmpl_ids):
                raise ValidationError(_("Please specify the product for which this rule should be applied"))
            elif item.applied_on == "0_product_variant" and not (item.product_id or item.product_ids):
                raise ValidationError(_("Please specify the product variant for which this rule should be applied"))

    @api.depends('applied_on', 'categ_id', 'product_tmpl_id','product_tmpl_ids', 'product_id','product_ids', 'compute_price', 'fixed_price', \
        'pricelist_id', 'percent_price', 'fixed_discount', 'price_discount', 'price_surcharge')
    def _get_pricelist_item_name_price(self):
        for item in self:
            if item.categ_id and item.applied_on == '2_product_category':
                item.name = _("Category: %s") % (item.categ_id.display_name)
            elif item.product_tmpl_id and item.applied_on == '1_product':
                item.name = _("Product: %s") % (item.product_tmpl_id.display_name)
            ###multi_product_variants
            elif item.product_tmpl_ids and item.applied_on == '1_product':
                for p_temp_id in item.product_tmpl_ids:
                    if len(item.product_tmpl_ids) > 1:
                        if item.compute_price == 'fixed' and item.fixed_price > 0.0:
                            item.name = _("Product: %s and others for fixed price %s") % (p_temp_id.name,item.fixed_price)
                        elif item.compute_price == 'fixed_discount':
                            item.name = _("Product: %s and others for %s fixed discount") % (p_temp_id.name,item.fixed_discount)
                        elif item.compute_price == 'percentage':
                            item.name = _("Product: %s and others for %s percent") % (p_temp_id.name,item.percent_price)
                        else:
                            item.name = _("Product: %s") % (p_temp_id.name)
                    else:
                        item.name = _("Product: %s") % (p_temp_id.name)
            elif item.product_id and item.applied_on == '0_product_variant':
                item.name = _("Variant: %s") % (item.product_id.with_context(display_default_code=False).display_name)
            ###multi_product_variants
            elif item.product_ids and item.applied_on == '0_product_variant':
                for p_variant_id in item.product_ids:
                    if len(item.product_ids) > 1:
                        if item.compute_price == 'fixed' and item.fixed_price > 0.0:
                            item.name = _("Variant: %s and others for fixed price %s") % (p_variant_id.name,item.fixed_price)
                        elif item.compute_price == 'fixed_discount':
                            item.name = _("Product: %s and others for %s fixed discount") % (p_variant_id.name,item.fixed_discount)
                        elif item.compute_price == 'percentage':
                            item.name = _("Variant: %s and others for %s percent") % (p_variant_id.name,item.percent_price)
                        else:
                            item.name = _("Variant: %s") % (p_variant_id.name)
                    else:
                        item.name = _("Variant: %s") % (p_variant_id.product_tmpl_id.name)
            else:
                item.name = _("All Products")

            if item.compute_price == 'fixed':
                decimal_places = self.env['decimal.precision'].precision_get('Product Price')
                if item.currency_id.position == 'after':
                    item.price = "%s %s" % (
                        float_repr(
                            item.fixed_price,
                            decimal_places,
                        ),
                        item.currency_id.symbol,
                    )
                else:
                    item.price = "%s %s" % (
                        item.currency_id.symbol,
                        float_repr(
                            item.fixed_price,
                            decimal_places,
                        ),
                    )
            elif item.compute_price == 'percentage':
                item.price = _("%s %% discount") % (item.percent_price)
            elif item.compute_price == 'fixed_discount':
                item.price = _("%s discount") % (item.fixed_discount)
            else:
                item.price = _("%s %% discount and %s surcharge") % (item.price_discount, item.price_surcharge)

    @api.onchange('compute_price')
    def _onchange_compute_price(self):
        if self.compute_price != 'fixed':
            self.fixed_price = 0.0
        if self.compute_price != 'fixed_discount':
            self.fixed_discount = 0.0
        if self.compute_price != 'percentage':
            self.percent_price = 0.0
        if self.compute_price != 'formula':
            self.update({
                'price_discount': 0.0,
                'price_surcharge': 0.0,
                'price_round': 0.0,
                'price_min_margin': 0.0,
                'price_max_margin': 0.0,
            })

    @api.onchange('product_id')
    def _onchange_product_id(self):
        has_product_id = self.filtered('product_id')
        for item in has_product_id:
            item.product_tmpl_id = item.product_id.product_tmpl_id
            ls_pid = []
            ls_pid.append(item.product_id.id)
            item.product_ids = [(6,0,ls_pid)]
        if self.env.context.get('default_applied_on', False) == '1_product':
            # If a product variant is specified, apply on variants instead
            # Reset if product variant is removed
            has_product_id.update({'applied_on': '0_product_variant'})
            (self - has_product_id).update({'applied_on': '1_product'})
            
    @api.onchange('product_ids')
    def _onchange_product_ids(self):
        has_product_ids = self.filtered('product_ids')
        for item in has_product_ids:
            ls_pid = []
            #for p_id in item.product_ids:
            #    item.product_tmpl_id = p_id.product_tmpl_id
            #    ls_pid.append(p_id.product_tmpl_id.id)            
            #item.product_tmpl_ids = [(6,0,ls_pid)]
            
        if self.env.context.get('default_applied_on', False) == '1_product':
            # If a product variant is specified, apply on variants instead
            # Reset if product variant is removed
            has_product_ids.update({'applied_on': '0_product_variant'})
            (self - has_product_ids).update({'applied_on': '1_product'})

    @api.onchange('product_tmpl_id')
    def _onchange_product_tmpl_id(self):
        has_tmpl_id = self.filtered('product_tmpl_id')
        for item in has_tmpl_id:
            if item.product_id and item.product_id.product_tmpl_id != item.product_tmpl_id:
                item.product_id = None
                
    @api.onchange('product_tmpl_ids')
    def _onchange_product_tmpl_ids(self):
        has_tmpl_ids = self.filtered('product_tmpl_ids')
        for item in has_tmpl_ids:
            if item.product_id and item.product_id.product_tmpl_id != item.product_tmpl_id:
                item.product_id = None

    @api.onchange('product_id', 'product_tmpl_id', 'categ_id')
    def _onchane_rule_content(self):
        if not self.user_has_groups('product.group_sale_pricelist') and not self.env.context.get('default_applied_on', False):
            # If advanced pricelists are disabled (applied_on field is not visible)
            # AND we aren't coming from a specific product template/variant.
            variants_rules = self.filtered('product_id')
            template_rules = (self-variants_rules).filtered('product_tmpl_id')
            variants_rules.update({'applied_on': '0_product_variant'})
            template_rules.update({'applied_on': '1_product'})
            (self-variants_rules-template_rules).update({'applied_on': '3_global'})

    def save_multi_record(self): 
                      
        for rec in self:
            if rec.isMulti_products and len(rec.product_tmpl_ids) >= 1:
                for values in rec.product_tmpl_ids:
                    self.env['product.pricelist.item'].create({'applied_on': rec.applied_on, 
                          'min_quantity': rec.min_quantity, 
                          'pricelist_id': rec.pricelist_id.id, 
                          'compute_price': rec.compute_price, 
                          'base': rec.base, 
                          'price_discount': rec.price_discount, 
                          'categ_id': rec.categ_id, 
                          'product_tmpl_id': values.id, 
                          'name': values.name, 
                          'isMulti_products': False, #self.isMulti_products, 
                          'website_deals_m2o': rec.website_deals_m2o, 
                          'isMulti_variants': False, #self.isMulti_variants, 
                          'date_start': rec.date_start, 
                          'date_end': rec.date_end, 
                          'fixed_price': rec.fixed_price, 
                          'fixed_discount': rec.fixed_discount, 
                          'percent_price': rec.percent_price, 
                          'price_surcharge': rec.price_surcharge, 
                          'price_round': rec.price_round, 
                          'price_min_margin': rec.price_min_margin, 
                          'price_max_margin': rec.price_max_margin,
                          'deal_applied_on': rec.deal_applied_on, 
                          'actual_price': rec.actual_price,
                          'discounted_price': rec.discounted_price,                         
                          'group_id': rec.id
                          })
                rec.sudo().write({'isGenerated': True})
            
            elif rec.isMulti_variants and len(rec.product_ids) >= 1:
                for values in rec.product_ids:
                    self.env['product.pricelist.item'].create({'applied_on': rec.applied_on, 
                          'min_quantity': rec.min_quantity, 
                          'pricelist_id': rec.pricelist_id.id, 
                          'compute_price': rec.compute_price, 
                          'base': rec.base, 
                          'price_discount': rec.price_discount, 
                          'categ_id': rec.categ_id, 
                          'product_id': values.id, 
                          'name': values.name, 
                          'isMulti_products': False, #self.isMulti_products, 
                          'website_deals_m2o': rec.website_deals_m2o, 
                          'isMulti_variants': False, #self.isMulti_variants, 
                          'date_start': rec.date_start, 
                          'date_end': rec.date_end, 
                          'fixed_price': rec.fixed_price, 
                          'fixed_discount': rec.fixed_discount, 
                          'percent_price': rec.percent_price, 
                          'price_surcharge': rec.price_surcharge, 
                          'price_round': rec.price_round, 
                          'price_min_margin': rec.price_min_margin, 
                          'price_max_margin': rec.price_max_margin,
                          'deal_applied_on': rec.deal_applied_on,
                          'actual_price': rec.actual_price,
                          'discounted_price': rec.discounted_price,
                          'group_id': rec.id
                          })
                rec.sudo().write({'isGenerated': True})

            
    @api.model_create_multi
    def create(self, vals_list):
        for values in vals_list:
            if values.get('isMulti_products', False):
                values['isMulti'] = values.get('isMulti_products')
            if values.get('isMulti_variants', False):
                values['isMulti'] = values.get('isMulti_variants')
            if values.get('website_deals_m2o') and (values.get('isMulti_products') or values.get('isMulti_products')):
                if self.id:
                    child_data = self.env['product.pricelist.item'].search([('group_id', '=', self.id)])
                    if child_data:
                        child_data.write({'website_deals_m2o': values.get('website_deals_m2o')})
                else:
                    raise UserError('Please click Generate button first for multi pricelist in deals item form.')
            if values.get('applied_on', False):
                # Ensure item consistency for later searches.
                applied_on = values['applied_on']
                if applied_on == '3_global':
                    values.update(dict(product_id=None, product_tmpl_id=None, categ_id=None))
                elif applied_on == '2_product_category':
                    values.update(dict(product_id=None, product_tmpl_id=None))
                elif applied_on == '1_product':                                
                    values.update(dict(product_id=None, categ_id=None))
                elif applied_on == '0_product_variant':
                    values.update(dict(categ_id=None))                
        return super(ProductPricelistItem, self).create(vals_list)

    def write(self, values):
        if values.get('isMulti_products'):
            values['isMulti'] = values.get('isMulti_products')
        if values.get('isMulti_variants'):
            values['isMulti'] = values.get('isMulti_variants')
        if values.get('website_deals_m2o'):
            for rec in self:
                child_data = self.env['product.pricelist.item'].search([('group_id', '=', rec.id)])
                for cd in child_data:
                    cd.write({'website_deals_m2o': values.get('website_deals_m2o')})
                    
        if self.group_id and values:
            child_data = self.env['product.pricelist.item'].search([('group_id', '=', self.id)])                
            for p_data in child_data:                   
                for v_data, k_data in values.items():
                    if v_data != 'product_tmpl_ids':
                        p_data.write({v_data : k_data})
         
        if values.get('applied_on', False):
            # Ensure item consistency for later searches.
            applied_on = values['applied_on']
            if applied_on == '3_global':
                values.update(dict(product_id=None, product_tmpl_id=None, categ_id=None))
            elif applied_on == '2_product_category':
                values.update(dict(product_id=None, product_tmpl_id=None))
            elif applied_on == '1_product':
                values.update(dict(product_id=None, categ_id=None))
            elif applied_on == '0_product_variant':
                values.update(dict(categ_id=None))
        res = super(ProductPricelistItem, self).write(values)
        # When the pricelist changes we need the product.template price
        # to be invalided and recomputed.
        self.flush()
        self.invalidate_cache()
        return res
    
class WebsiteDeals(models.Model):
    _name = 'website.deals'
    _description = 'Website Deals'
    _order = "sequence"

    @api.model
    def _get_default_pricelist(self):
        irDefault = self.env['ir.default'].sudo()
        deal_pricelist = irDefault.get('website.daily.deals.conf', 'deal_pricelist')
        return deal_pricelist

    name = fields.Char(string='Name', required=True)
    title = fields.Char(string='Title', required=True, help="title of the deal to show in website",
                        default="Get a heavy discount on this season")
    show_title = fields.Boolean('Show Title In Website',
                                help="the title will be displayed in the website and it is displayed only if 'What to Display in Website = Products Only'")
    description = fields.Text(string='Description', help="description of the deal to show in website")
    state = fields.Selection(
        [('draft', 'Draft'), ('pending', 'Pending For Approval'), ('validated', 'In Progress'), ('expired', 'Expired'), ('cancel', 'Cancelled')], 'State',
        default='draft')
    deal_pricelist = fields.Many2one('product.pricelist', 'Pricelist', domain="[('active','=', True),('selectable','=', True)]", required=True, default=_get_default_pricelist)
    overide_config = fields.Boolean('Override Default Configuration')
    start_date = fields.Datetime('Start Date', required=True, default=datetime.now() + timedelta(days=-1))
    end_date = fields.Datetime('End Date', required=True, default=datetime.now() + timedelta(days=1))
    expiration_status = fields.Selection(
        [('planned', "Planned"), ('inprogress', "In Progress"), ('expired', "Expired")],
        compute='_compute_expiration_status', search='_search_by_expiration_status'
    )

    banner = fields.Binary('Banner', required=False)
    pricelist_items = fields.One2many(comodel_name='product.pricelist.item', inverse_name='website_deals_m2o',
                                      string='Products')
    display_products_as = fields.Selection([('grid', 'Grid'), ('slider', 'Slider')],
                                           'How to display Products in Website', default='grid',
                                           help="choose how to display the produts in website.")
    item_to_show = fields.Selection(
        [('banner_only', 'Banner Only'), ('products_only', 'Products Only'), ('both', 'Both')],
        'What to Display in Website', default='both', help="choose what you want to display in website.")

    show_message_before_expiry = fields.Boolean('Show Message before Expiry',
                                                help="Do you want to show a message before the expiry date of the deal, if yes then set this true.")
    message_before_expiry = fields.Char('Message before Expiry',
                                        help="The message you want to show in the website when deal is about to expire.",
                                        default='Hurry Up!!! This deal is about to expire.')
    interval_before = fields.Integer('Time interval before to display message',
                                     help="How much time before the expiry date you want to display the message.",
                                     default=1)
    unit_of_time = fields.Selection([('minutes', 'Minutes'), ('hours', 'Hours'), ('days', 'Days'), ('weeks', 'Weeks')],
                                    'Time Unit', required=True, default='hours')

    show_message_after_expiry = fields.Boolean('Show Message After Expiry',
                                               help="Do you want to show the message after the expiry date of the deal.")
    message_after_expiry = fields.Char('Message After Expiry',
                                       help="The message you want to show in the website when deal is expired.",
                                       default='Opps!! This deal has been expired.')
    d_state_after_expire = fields.Selection([('blur', 'Blur'), ('delete', 'Delete')],
                                            'What to do with deal after Expiry', default='delete', readonly=True,
                                            help="What do you want to do with deal after expiration.Either you can blur the deals in website or delete a deal from website")
    display_on_homepage = fields.Boolean(string='Display on Homepage', default=False, attrs="{'readonly': [('forbidden_user', '=', uid)]")
    sequence = fields.Integer(string='Sequence', default=30, required=True)
    # user_id = fields.Char("User ID", default=lambda self: self.env.user.id)
    seller_name = fields.Char("Seller", default=lambda self: self.env.user.name)

    @api.depends('start_date', 'end_date')
    def _compute_expiration_status(self):
        for record in self:
            current_time = datetime.now()
            if current_time < record.start_date:
                record.expiration_status = 'planned'
            elif record.start_date <= current_time <= record.end_date:
                record.expiration_status = 'inprogress'
            else:
                record.expiration_status = 'expired'

    def _search_by_expiration_status(self, operator, value):
        if value == 'planned':
            return self._search_by_planned(operator)
        elif value == 'inprogress':
            return self._search_by_inprogress(operator)
        else:
            return self._search_by_expired(operator)

    def _search_by_planned(self, operator):
        current_time = datetime.now()
        if operator == '=':
            return [('start_date', '>', current_time)]
        elif operator == '!=':
            return [('start_date', '<=', current_time)]

    def _search_by_inprogress(self, operator):
        current_time = datetime.now()
        if operator == '=':
            return [('start_date', '<=', current_time), ('end_date', '>=', current_time)]
        elif operator == '!=':
            return ['|', ('start_date', '>', current_time), ('end_date', '<', current_time)]

    def _search_by_expired(self, operator):
        current_time = datetime.now()
        if operator == '=':
            return [('end_date', '<', current_time)]
        if operator == '!=':
            return [('end_date', '>=', current_time)]

    @api.constrains('sequence')
    def _check_value(self):
        if self.sequence <= 0:
            raise ValidationError('Enter the sequence value greater than 0')

    @api.model
    def create(self, vals):
        
        if vals.get("marketplace_seller_id"):
            seller_obj = self.env['res.partner'].sudo().browse(int(vals.get("marketplace_seller_id")))
            vals["seller_name"] = seller_obj.name
            
        return super(WebsiteDeals, self).create(vals)

    def write(self, values):
        
        if values.get("marketplace_seller_id"):
            seller_obj = self.env['res.partner'].sudo().browse(int(values.get("marketplace_seller_id")))
            values["seller_name"] = seller_obj.name
            
        return super(WebsiteDeals, self).write(values)

    @api.model
    def _update_deal_items(self):
        pricelist = self.deal_pricelist
        if pricelist and self.state == 'validated':
            for item in self.pricelist_items:
                item.pricelist_id = pricelist.id
                if item.product_tmpl_id:
                    price = pricelist.get_product_price(item.product_tmpl_id, 1, None)

                elif item.product_id:
                    price = pricelist.get_product_price(item.product_id, 1, None)
                else:
                    price = 0.0
                item.discounted_price = price
        else:
            for item in self.pricelist_items:
                item.pricelist_id = self.env.ref("website_daily_deals.wk_deals_dummy_pricelist")

    def get_instock_items(self):
        instock_items = []
        for item in self.pricelist_items:
            product_id = item.product_tmpl_id if item.product_tmpl_id else item.product_id.product_tmpl_id
            product_quantity = self.env['website'].get_product_stock_qty(product_id.sudo(), self.env['website'].get_config_settings_values().get('wk_stock_type'))
            if product_quantity > 0:
                instock_items.append(item)
        return instock_items

    @api.onchange('interval_before')
    def onchange_deal_interval_before(self):
        if self.interval_before == 0:
            self.interval_before = 1

    @api.onchange('deal_pricelist', 'start_date', 'end_date', 'overide_config', 'pricelist_items')
    def onchange_deal_config(self):
        self.set_to_draft()

    def set_to_draft(self):
        self.state = 'draft'
        self._update_deal_items()

    def set_to_expired(self):
        # self.state = 'expired'
        self._update_deal_items()

    def button_validate_the_deal(self):
        start_date = self.start_date
        end_date = self.end_date
        print("end date = ", end_date)
        if start_date > end_date:
            raise UserError('End date can not be earlier than start date.')
        else:
            self.state = 'validated'
            self._update_deal_items()

    def cancel_deal(self):
        self.state = 'cancel'
        self._update_deal_items()

    @api.model
    def get_valid_deals(self):

        deals = self.search([
            '&', ('state', '=', 'validated'),
                '|', ('expiration_status', '=', 'inprogress'),
                    '&', ('expiration_status', '=', 'expired'), ('d_state_after_expire', '!=', 'delete')
        ]).sorted(lambda d: d.expiration_status == 'expired')

        return deals

    @api.model
    def get_homepage_deals(self):
        deals = self.search([
            '&', ('state', '=', 'validated'),
                ('display_on_homepage', '=', True),
                '|', ('expiration_status', '=', 'inprogress'),
                    '&', ('expiration_status', '=', 'expired'), ('d_state_after_expire', '!=', 'delete')
        ]).sorted(lambda d: d.expiration_status == 'expired')

        return deals

    @api.model
    def get_page_header(self):
        irDefault = self.env['ir.default'].sudo()
        show_header = irDefault.get('website.daily.deals.conf', 'show_page_header')
        return show_header and irDefault.get('website.daily.deals.conf', 'page_header_text')

    @api.model
    def is_deal_banner_shown(self):
        if self.overide_config:
            return self.item_to_show == 'banner_only' or self.item_to_show == 'both'
        else:
            config_value = self.env['ir.default'].sudo().get('website.daily.deals.conf', 'item_to_show')
            return config_value == 'banner_only' or config_value == 'both'
        return False

    # @api.model
    # def button_apply_this_pricelist(self,*args):
    # 	msg = "By applying this pricelist the currently applied pricelist of website will be removed and this pricelist will be active on current website."
    # 	return self.show_msg_wizard(msg)

    def show_msg_wizard(self, msg):
        res_id = self.env['deal.wizard.message'].create({'msg': msg})
        modal = {
            'domain': "[]",
            'name': 'Warning',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'deal.wizard.message',
            'type': 'ir.actions.act_window',
            # 'context': {'feature_id': feature.id},
            'res_id': res_id.id,
            'view_id': self.env.ref('website_daily_deals.website_deal_wizard_pricelist_warning_form_view').id,
            'target': 'new',
        }
        return modal

    @api.model
    def is_deal_product_shown(self):
        if self.overide_config:
            return self.item_to_show == 'products_only' or self.item_to_show == 'both'
        else:
            config_value = self.env['ir.default'].sudo().get('website.daily.deals.conf', 'item_to_show')
            return config_value == 'products_only' or config_value == 'both'
        return False

    @api.model
    def get_display_products_as(self):
        if self.overide_config:
            return self.display_products_as
        else:
            config_value = self.env['ir.default'].sudo().get('website.daily.deals.conf', 'display_products_as')
            return config_value
        return "grid"

    @api.model
    def state_after_expiration(self):
        if self.overide_config:
            return self.expiration_status == 'expired' and self.d_state_after_expire
        else:
            config_value = self.env['ir.default'].sudo().get('website.daily.deals.conf', 'd_state_after_expire')
            return self.expiration_status == 'expired' and config_value and 'blur'
        return False


    @api.model
    def get_message_before_expiry_and_offset(self):
        message = False
        td = False
        if self.state == "validated":
            if self.overide_config:

                if self.show_message_before_expiry:
                    message = self.message_before_expiry
                    interval = self.interval_before
                    unit = self.unit_of_time
                    td = self.get_time_delta(interval, unit)
            else:
                IrDefault = self.env['ir.default'].sudo()
                if IrDefault.get('website.daily.deals.conf', 'show_message_before_expiry'):
                    message = IrDefault.get('website.daily.deals.conf', 'message_before_expiry')
                    interval = IrDefault.get('website.daily.deals.conf', 'show_message_before_expiry')
                    unit = IrDefault.get('website.daily.deals.conf', 'show_message_before_expiry')
                    td = self.get_time_delta(interval, unit)

        return {'message': message, 'offset': td and self.end_date - td}

    @api.model
    def get_time_delta(self, interval, unit):
        if interval and unit:
            if unit == "minutes":
                td = timedelta(minutes=int(interval))
            elif unit == "hours":
                td = timedelta(hours=int(interval))
            elif unit == "days":
                td = timedelta(days=int(interval))
            elif unit == "weeks":
                td = timedelta(weeks=int(interval))
            elif unit == "months":
                td = timedelta(months=int(interval))
            else:
                td = timedelta(hours=1)

            return td
        return False

    @api.model
    def get_message_after_expiry(self):
        message = False
        if self.expiration_status == 'expired':
            if self.overide_config:
                message = self.show_message_after_expiry and self.message_after_expiry
            else:
                IrDefault = self.env['ir.default'].sudo()
                message = IrDefault.get('website.daily.deals.conf', 'show_message_after_expiry') and IrDefault.get(
                    'website.daily.deals.conf', 'message_after_expiry')
        return message

    def action_request(self):
        super(WebsiteDeals, self).write({'state': 'pending'})


# class WebsiteDeals(models.Model):
#     _inherit = 'website.deals'
#
#     state = fields.Selection(selection_add=[('pending', 'Pending For Approval')])
# method for frontend contollers

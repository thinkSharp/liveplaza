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

from itertools import chain


class ProductPricelist(models.Model):
    _inherit = "product.pricelist"

    def unlink(self):
        if self.name == "Deals Dummy Pricelist":
            raise UserError('This Pricelist Can Not be deleted as this is used by website daily deals Module.')
        else:
            return super(ProductPricelist, self).unlink();


class ProductPricelistItem(models.Model):
    _inherit = "product.pricelist.item"

    website_deals_m2o = fields.Many2one('website.deals', 'Corresponding Deal', help="My Deals", ondelete="cascade")
    actual_price = fields.Float(related='product_tmpl_id.list_price', string='Actual Price', store=True)
    discounted_price = fields.Float('Discounted Price', default=0.0)
    website_size_x = fields.Integer('Size X', default=2)
    website_size_y = fields.Integer('Size Y', default=2)
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

    @api.onchange('deal_applied_on')
    @api.depends('deal_applied_on')
    def onchange_deal_applied_on(self):
        self.applied_on = self.deal_applied_on
        self.pricelist_id = self.website_deals_m2o.deal_pricelist
        self.min_quantity = 1

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
        'pricelist_id', 'percent_price', 'price_discount', 'price_surcharge')
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
            else:
                item.price = _("%s %% discount and %s surcharge") % (item.price_discount, item.price_surcharge)

    @api.onchange('compute_price')
    def _onchange_compute_price(self):
        if self.compute_price != 'fixed':
            self.fixed_price = 0.0
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
                child_data = self.env['product.pricelist.item'].search([('group_id', '=', rec.id)])
                if child_data:
                    child_data_list = []
                    child_p_list = []
                    for cdata in child_data:
                        child_data_list.append(cdata)
                        child_p_list.append(cdata.product_tmpl_id)
                        
                    if len(rec.product_tmpl_ids) > len(child_data):                    
                        for values in rec.product_tmpl_ids:
                            if values not in child_p_list:
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
                                      #'product_id': rec.product_id, 
                                      'isMulti_variants': False, #self.isMulti_variants, 
                                      'date_start': rec.date_start, 
                                      'date_end': rec.date_end, 
                                      'fixed_price': rec.fixed_price, 
                                      'percent_price': rec.percent_price, 
                                      'price_surcharge': rec.price_surcharge, 
                                      'price_round': rec.price_round, 
                                      'price_min_margin': rec.price_min_margin, 
                                      'price_max_margin': rec.price_max_margin,
                                      'group_id': rec.id
                                      })
                        rec.sudo().write({'isGenerated': True})
                    elif len(rec.product_tmpl_ids) < len(child_data):
                        for clist in child_data_list:                            
                            if clist.product_tmpl_id not in rec.product_tmpl_ids:
                                clist.unlink()                                
                else:
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
                              #'product_id': rec.product_id, 
                              'isMulti_variants': False, #self.isMulti_variants, 
                              'date_start': rec.date_start, 
                              'date_end': rec.date_end, 
                              'fixed_price': rec.fixed_price, 
                              'percent_price': rec.percent_price, 
                              'price_surcharge': rec.price_surcharge, 
                              'price_round': rec.price_round, 
                              'price_min_margin': rec.price_min_margin, 
                              'price_max_margin': rec.price_max_margin,
                              'group_id': rec.id
                              })
                rec.sudo().write({'isGenerated': True})
            
            elif rec.isMulti_variants and len(rec.product_ids) >= 1:
                
                child_data = self.env['product.pricelist.item'].search([('group_id', '=', rec.id)])
                if child_data:
                    child_data_list = []
                    child_p_list = []
                    for cdata in child_data:
                        child_data_list.append(cdata)
                        child_p_list.append(cdata.product_id)
                        
                    if len(rec.product_ids) > len(child_data):                    
                        for values in rec.product_ids:
                            if values not in child_p_list:
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
                                      #'product_id': rec.product_id, 
                                      'isMulti_variants': False, #self.isMulti_variants, 
                                      'date_start': rec.date_start, 
                                      'date_end': rec.date_end, 
                                      'fixed_price': rec.fixed_price, 
                                      'percent_price': rec.percent_price, 
                                      'price_surcharge': rec.price_surcharge, 
                                      'price_round': rec.price_round, 
                                      'price_min_margin': rec.price_min_margin, 
                                      'price_max_margin': rec.price_max_margin,
                                      'group_id': rec.id
                                      })
                        rec.sudo().write({'isGenerated': True})
                    elif len(rec.product_ids) < len(child_data):
                        for clist in child_data_list:                            
                            if clist.product_id not in rec.product_ids:
                                clist.unlink()                                
                else:
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
                              #'product_id': rec.product_id, 
                              'isMulti_variants': False, #self.isMulti_variants, 
                              'date_start': rec.date_start, 
                              'date_end': rec.date_end, 
                              'fixed_price': rec.fixed_price, 
                              'percent_price': rec.percent_price, 
                              'price_surcharge': rec.price_surcharge, 
                              'price_round': rec.price_round, 
                              'price_min_margin': rec.price_min_margin, 
                              'price_max_margin': rec.price_max_margin,
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
                
        if (self.isMulti_products or self.isMulti_variants) and (values.get('product_tmpl_ids') or values.get('product_ids')):
            values['isGenerated'] = False
                    
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
    deal_pricelist = fields.Many2one('product.pricelist', 'Pricelist', required=True, default=_get_default_pricelist)
    overide_config = fields.Boolean('Override Default Configuration')
    start_date = fields.Datetime('Start Date', required=True, default=datetime.now() + timedelta(days=-1))
    end_date = fields.Datetime('End Date', required=True, default=datetime.now() + timedelta(days=1))

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
                                            'What to do with deal after Expiry', default='blur',
                                            help="What do you want to do with deal after expiration.Either you can blur the deals in website or delete a deal from website")
    display_on_homepage = fields.Boolean(string='Display on Homepage', default=False, attrs="{'readonly': [('forbidden_user', '=', uid)]")
    sequence = fields.Integer(string='Sequence', default=30, required=True)
    # user_id = fields.Char("User ID", default=lambda self: self.env.user.id)
    seller_name = fields.Char("Seller", default=lambda self: self.env.user.name)

    @api.constrains('sequence')
    def _check_value(self):
        if self.sequence <= 0:
            raise ValidationError('Enter the sequence value greater than 0')

    @api.model
    def create(self, vals):
        # if not vals.get('banner'):
        #	raise UserError('No banner chosen, please choose a banner before saving.')
        return super(WebsiteDeals, self).create(vals)

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
        self.state = 'expired'
        self._update_deal_items()

    def button_validate_the_deal(self):
        start_date = self.start_date
        end_date = self.end_date
        print("end date = ", end_date)
        if start_date > end_date:
            raise UserError('End date can not be earlier than start date.')
        elif end_date > datetime.now():
            self.state = 'validated'
            self._update_deal_items()
        else:
            self.set_to_expired()

    def cancel_deal(self):
        self.state = 'cancel'
        self._update_deal_items()

    @api.model
    def get_valid_deals(self):

        deals = self.search(['|', ('state', '=', 'validated'),
                             '&', ('state', '=', 'expired'), ('d_state_after_expire', '!=', 'delete')]).sorted(
            lambda d: d.state == "expired")

        return deals

    @api.model
    def get_homepage_deals(self):
        deals = self.search([('state', 'in', ['validated']), ('display_on_homepage', '=', 'True')])
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
            return self.state == 'expired' and self.d_state_after_expire
        else:
            config_value = self.env['ir.default'].sudo().get('website.daily.deals.conf', 'd_state_after_expire')
            return self.state == 'expired' and config_value and 'blur'
        return False

    @api.onchange('datetime.now()')
    def cancel_expired_deals(self):
        if datetime.now() > self.end_date + timedelta(seconds=10):
            self.cancel_deal()
            return

    @api.model
    def cancel_expired_deals(self):
        if datetime.now() > self.end_date + timedelta(seconds=10):
            self.cancel_deal()
            return


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
        if self.state == "expired":
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

# -*- coding: utf-8 -*-
################################################################################
#
#   Copyright (c) 2016-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>)
#
################################################################################

import logging

from odoo import _, api, fields, models
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)

class FacebookShop(models.Model):
    _inherit = 'fb.facebook.shop'

    @api.model
    def _set_seller_id(self):
        user_obj = self.env['res.users'].sudo().browse(self._uid)
        if user_obj.partner_id and user_obj.partner_id.seller:
            return user_obj.partner_id.id
        return self.env['res.partner']

    def _get_default_domain(self):
        domain = super(FacebookShop,self)._get_default_domain()
        if self._context.get('mp_fb_feed'):
            domain.append(('marketplace_seller_id','in',self.compute_login_userid()))
        return domain

    website_id = fields.Many2one(default=lambda self:self.env['website'].get_current_website())
    shop_url = fields.Char(default=lambda self:self.env['ir.config_parameter'].sudo().get_param('web.base.url'))
    marketplace_seller_id = fields.Many2one('res.partner', string='Seller', default=_set_seller_id)

    @api.onchange('marketplace_seller_id')
    def product_domain(self):
        if self.marketplace_seller_id:
            self.warehouse_id = self.marketplace_seller_id.warehouse_id
            return {
                'domain':{'product_ids_rel':[('marketplace_seller_id','=',self.marketplace_seller_id.id),('status','=','approved')]}
            }
        else:
            return False
    def compute_login_userid(self):
        login_ids = []
        seller_group = self.env['ir.model.data'].get_object_reference(
            'odoo_marketplace', 'marketplace_seller_group')[1]
        officer_group = self.env['ir.model.data'].get_object_reference(
            'odoo_marketplace', 'marketplace_officer_group')[1]
        groups_ids = self.env.user.sudo().groups_id.ids
        if seller_group in groups_ids and officer_group not in groups_ids:
            login_ids.append(self.env.user.sudo().partner_id.id)
            return login_ids
        elif seller_group in groups_ids and officer_group in groups_ids:
            obj = self.env['res.partner'].search([('seller','=',True)])
            for rec in obj:
                login_ids.append(rec.id)
            return login_ids

    def _store_data(self,final_xml):
        if self._context.get('mp_fb_feed'):
            return super(FacebookShop,self.sudo())._store_data(final_xml)
        return super(FacebookShop,self)._store_data(final_xml)

    @api.model
    def create(self,vals):
        if self._context.get('mp_fb_feed'):
            lang = vals.get('content_language_id')
            prev_rec = self.env['fb.facebook.shop'].sudo().search([
            ('marketplace_seller_id','=',vals.get('marketplace_seller_id')),
            ('content_language_id','=',lang)])
            if prev_rec.exists():
                raise UserError(_('Catalog with this Content language already exists'))
        return super(FacebookShop,self).create(vals)

    def write(self,vals):
        if self._context.get('mp_fb_feed') and vals.get('content_language_id') or vals.get('marketplace_seller_id') :
            lang = vals.get('content_language_id') or self.content_language_id.id
            seller_id = vals.get('marketplace_seller_id') or self.marketplace_seller_id.id
            prev_rec = self.env['fb.facebook.shop'].sudo().search([
                ('id','!=',self.id),
                ('marketplace_seller_id','=',seller_id),
                ('content_language_id','=',lang)])
            if prev_rec.exists():
                raise UserError(_('Catalog with this Content language already exists'))
        return super(FacebookShop,self).write(vals)

class FacebookAttachment(models.Model):
    _inherit = 'fb.attachment.mapping'

    @api.model
    def _set_seller_id(self):
        user_obj = self.env['res.users'].sudo().browse(self._uid)
        if user_obj.partner_id and user_obj.partner_id.seller:
            return user_obj.partner_id.id
        return self.env['res.partner']

    marketplace_seller_id = fields.Many2one('res.partner', string='Seller', default=_set_seller_id)

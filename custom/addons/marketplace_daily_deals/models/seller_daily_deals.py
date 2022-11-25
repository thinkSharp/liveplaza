# -*- coding: utf-8 -*-
#################################################################################
# Author      : Webkul Software Pvt. Ltd. (<https://webkul.com/>)
# Copyright(c): 2015-Present Webkul Software Pvt. Ltd.
# License URL : https://store.webkul.com/license.html/
# All Rights Reserved.
#
#
#
# This program is copyright property of the author mentioned above.
# You can`t redistribute it and/or modify it.
#
#
# You should have received a copy of the License along with this program.
# If not, see <https://store.webkul.com/license.html/>
#################################################################################

from odoo import models,fields,api,_
import logging
_logger = logging.getLogger(__name__)

class WebsiteDeals(models.Model):
    _inherit = 'website.deals'

    @api.model
    def _set_seller_id(self):
        user_obj = self.env['res.users'].sudo().browse(self._uid)
        if user_obj.partner_id and user_obj.partner_id.seller:
            if not user_obj.has_group('base.group_system'):
                return user_obj.partner_id.id
            else:
                return self.env['res.partner']
        return self.env['res.partner']

    marketplace_seller_id = fields.Many2one("res.partner", string="Seller", default=_set_seller_id, copy=False) #default=_set_seller_id,

class product_pricelist_item(models.Model):
    _inherit = 'product.pricelist.item'

    @api.onchange('product_tmpl_id')
    def _set_product_template(self):
        if self._context.get('mp_seller_deal'):
            login_ids = []
            seller_group = self.env['ir.model.data'].get_object_reference(
                'odoo_marketplace', 'marketplace_seller_group')[1]
            officer_group = self.env['ir.model.data'].get_object_reference(
                'odoo_marketplace', 'marketplace_officer_group')[1]
            groups_ids = self.env.user.sudo().groups_id.ids
            if seller_group in groups_ids and officer_group not in groups_ids:
                login_ids.append(self.env.user.sudo().partner_id.id)
                marketplace_seller_id = self.env.user.sudo().partner_id.id
            elif seller_group in groups_ids and officer_group in groups_ids:
                login_ids.append(self.website_deals_m2o.marketplace_seller_id.id)
            domain = {'product_tmpl_id': [('marketplace_seller_id','in',login_ids),('status','=','approved'),('website_published','!=',False)]}
            return {'domain':domain}
        return self.env['product.template']

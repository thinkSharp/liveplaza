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

class VoucherHistory(models.Model):
    _inherit = "voucher.history"

    marketplace_seller_id = fields.Many2one("res.partner", string="Seller")

    @api.model
    def create(self, vals):
        res  = super(VoucherHistory, self).create(vals)
        res.marketplace_seller_id = res.voucher_id.marketplace_seller_id.id
        return res

class VoucherVoucher(models.Model):
    _inherit = "voucher.voucher"

    # @api.model
    # def _set_seller_id(self):
    #     user_obj = self.env['res.users'].sudo().browse(self._uid)
    #     if user_obj.partner_id and user_obj.partner_id.seller:
    #         return user_obj.partner_id.id
    #     return self.env['res.partner']

    @api.model
    def _set_seller_id(self):
        user_obj = self.env['res.users'].sudo().browse(self._uid)
        if user_obj.partner_id and user_obj.partner_id.seller:
            if not user_obj.has_group('base.group_system'):
                return user_obj.partner_id.id
            else:
                return self.env['res.partner']
        return self.env['res.partner']

    marketplace_seller_id = fields.Many2one("res.partner", string="Seller", default=_set_seller_id, copy=False)

    seller_product_ids = fields.Many2many('product.template', compute="get_seller_products")

    product_ids = fields.Many2many('product.template', 'voucher_id', 'product_id', 'voucher_product_rel',
        string='Products',
        help="Add products on which this voucher will be valid",
        domain = lambda self: [('marketplace_seller_id','in',self.env['voucher.voucher'].compute_login_userid()),('status','=','approved')] if self._context.get('mp_gift_voucher') else [],
        )

    @api.onchange('marketplace_seller_id')
    def get_seller_products(self):
        for rec in self:
            if rec.marketplace_seller_id:
                products = self.env['product.template'].search([('status', '=', 'approved'), ('active', '=', True),
                            ('marketplace_seller_id', '=', rec.marketplace_seller_id.id)])
                rec.seller_product_ids = products
            else:
                print("no seller id")
                products = self.env['product.template'].search([('status', '=', 'approved'), ('active', '=', True)])
                rec.seller_product_ids = products

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
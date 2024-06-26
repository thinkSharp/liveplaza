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
# Resolve Conflict Production Server

from odoo import models, fields, api, _


class marketplace_dashboard(models.Model):
    _name = "marketplace.dashboard"
    _description = "Marketplace Dashboard"

    def is_user_seller(self):
        # Works with singal id
        seller_group = self.env['ir.model.data'].get_object_reference(
            'odoo_marketplace', 'marketplace_draft_seller_group')[1]
        manager_group = self.env['ir.model.data'].get_object_reference(
            'odoo_marketplace', 'marketplace_officer_group')[1]
        groups_ids = self.env.user.sudo().groups_id.ids
        if seller_group in groups_ids and manager_group in groups_ids:
            return False
        if seller_group in groups_ids and manager_group not in groups_ids:
            return True

    def _is_seller_or_manager(self):
        for rec in self:
            is_seller = False
            if rec._uid:
                seller_groups = self.env['ir.model.data'].sudo().xmlid_to_object('odoo_marketplace.marketplace_seller_group')
                manager_group = self.env['ir.model.data'].sudo().xmlid_to_object('odoo_marketplace.marketplace_officer_group')
                if rec._uid in seller_groups.users.ids:
                    is_seller = True
                if rec._uid in manager_group.users.ids:
                    is_seller = False
            rec.is_seller = is_seller

    def _get_approved_count(self):
        for rec in self:
            if rec.state == 'product':
                if rec.is_user_seller():
                    obj = self.env['product.template'].search(
                        [('marketplace_seller_id.user_ids', '=', self._uid), ('status', '=', 'approved')])
                else:
                    obj = self.env['product.template'].search(
                        [('marketplace_seller_id', '!=', False), ('status', '=', 'approved')])
                rec.count_product_approved = len(obj)
                rec.count_product_ready = 0
            elif rec.state == 'seller':
                obj = self.env['res.partner'].search(
                    [('seller', '=', True), ('state', '=', 'approved')])
                rec.count_product_approved = len(obj)
                rec.count_product_ready = 0
            elif rec.state == 'order':
                if rec.is_seller:
                    user_obj = self.env['res.users'].browse(rec._uid)
                    # obj = self.env['sale.order.line'].search( [('marketplace_seller_id', '=',
                    # user_obj.partner_id.id), ('marketplace_state', '=', 'approved'),('state', 'not in', ('draft',
                    # 'sent'))])
                    obj = self.env['sale.order.line'].search(
                        [('marketplace_seller_id', '=', user_obj.partner_id.id), ('state', '=', 'ready_to_pick')])
                else:
                    # obj = self.env['sale.order.line'].search( [('marketplace_seller_id', '!=', False),
                    # ('marketplace_state', '=', 'approved'),('state', 'not in', ('draft', 'sent'))])
                    obj = self.env['sale.order.line'].search(
                        [('marketplace_seller_id', '!=', False), ('state', '=', 'ready_to_pick')])
                rec.count_product_approved = len(obj)
                rec.count_product_ready = len(obj)
            elif rec.state == 'payment':
                obj = self.env['seller.payment'].search(
                    [('seller_id', '!=', False), ('state', '=', 'posted')])
                rec.count_product_approved = len(obj)
                rec.count_product_ready = 0
            else:
                rec.count_product_approved = 0
                rec.count_product_ready = 0

    def _get_pending_count(self):
        for rec in self:
            if rec.state == 'product':
                if rec.is_user_seller():
                    obj = self.env['product.template'].search(
                        [('marketplace_seller_id.user_ids', '=', rec._uid), ('status', '=', 'pending')])
                else:
                    obj = self.env['product.template'].search(
                        [('marketplace_seller_id', '!=', False), ('status', '=', 'pending')])
                rec.count_product_pending = len(obj)
            elif rec.state == 'seller':
                obj = self.env['res.partner'].search(
                    [('seller', '=', True), ('state', '=', 'pending')])
                rec.count_product_pending = len(obj)
            elif rec.state == 'order':
                user_obj = self.env['res.users'].browse(rec._uid)
                if rec.is_seller:
                    # obj = self.env['sale.order.line'].search( [('marketplace_seller_id', '=',
                    # user_obj.partner_id.id), ('marketplace_state', '=', 'new'),('state', 'not in', ('draft',
                    # 'sent'))])
                    obj = self.env['sale.order.line'].search(
                        [('marketplace_seller_id', '=', user_obj.partner_id.id), ('state', 'in', ('sale', 'approve_by_admin'))])
                else:
                    # obj = self.env['sale.order.line'].search( [('marketplace_seller_id', '!=', False),
                    # ('marketplace_state', '=', 'new'),('state', 'not in', ('draft', 'sent'))])
                    obj = self.env['sale.order.line'].search(
                        [('marketplace_seller_id', '!=', False), ('state', 'in', ('sale', 'approve_by_admin'))])
                rec.count_product_pending = len(obj)
            elif rec.state == 'payment':
                obj = self.env['seller.payment'].search(
                    [('seller_id', '!=', False), ('state', '=', 'requested')])
                rec.count_product_pending = len(obj)
            else:
                rec.count_product_pending = 0

    def _get_rejected_count(self):
        for rec in self:
            if rec.state == 'product':
                if rec.is_user_seller():
                    obj = self.env['product.template'].search(
                        [('marketplace_seller_id.user_ids', '=', rec._uid), ('status', '=', 'rejected')])
                else:
                    obj = self.env['product.template'].search(
                        [('marketplace_seller_id', '!=', False), ('status', '=', 'rejected')])
                rec.count_product_rejected = len(obj)
            elif rec.state == 'seller':
                obj = self.env['res.partner'].search(
                    [('seller', '=', True), ('state', '=', 'denied')])
                rec.count_product_rejected = len(obj)
            elif rec.state == 'order':
                user_obj = self.env['res.users'].browse(rec._uid)
                if rec.is_seller:
                    # obj = self.env['sale.order.line'].search( [('marketplace_seller_id', '=',
                    # user_obj.partner_id.id), ('marketplace_state', '=', 'shipped'),('state', 'not in', ('draft',
                    # 'sent'))])
                    obj = self.env['sale.order.line'].search(
                        [('marketplace_seller_id', '=', user_obj.partner_id.id), ('state', '=', 'done')])
                else:
                    # obj = self.env['sale.order.line'].search(
                    #     [('marketplace_seller_id', '!=', False), ('marketplace_state', '=', 'shipped'),('state', 'not in', ('draft', 'sent'))])
                    obj = self.env['sale.order.line'].search(
                        [('marketplace_seller_id', '!=', False), ('state', '=', 'done')])
                rec.count_product_rejected = len(obj)
            elif rec.state == 'payment':
                obj = self.env['seller.payment'].search(
                    [('seller_id', '!=', False), ('state', '=', 'confirm'), ('payment_mode', '=', 'seller_payment')])
                rec.count_product_rejected = len(obj)
            else:
                rec.count_product_rejected = 0

    def _get_total_count(self):
        for record in self:
            record.count_total = sum([
                record.count_product_approved,
                record.count_product_rejected,
                record.count_product_pending,
            ])

    def _get_short_name(self):
        for record in self:
            record.short_name = ({
                'product': "Products",
                'seller': "Sellers",
                'order': "Orders",
                'payment': "Payments",
            })[record.state]

    color = fields.Integer(string='Color Index')
    name = fields.Char(string="Name", translate=True)
    state = fields.Selection(
        [('product', 'Product'), ('seller', 'Seller'), ('order', 'Order'), ('payment', 'Payment')])
    count_product_approved = fields.Integer(compute='_get_approved_count')
    count_product_pending = fields.Integer(compute='_get_pending_count')
    count_product_rejected = fields.Integer(compute='_get_rejected_count')
    count_total = fields.Integer(compute='_get_total_count')
    is_seller = fields.Boolean(compute="_is_seller_or_manager")
    short_name = fields.Char(compute='_get_short_name')


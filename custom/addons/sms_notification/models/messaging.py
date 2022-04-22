# -*- coding: utf-8 -*-
##########################################################################
# Author      : Webkul Software Pvt. Ltd. (<https://webkul.com/>)
# Copyright(c): 2017-Present Webkul Software Pvt. Ltd.
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
##########################################################################

from odoo import models, fields, api, _

import logging

_logger = logging.getLogger(__name__)


class SaleOrder(models.Model):
    _inherit = "sale.order"

    # def action_confirm(self):
    #     self.ensure_one()
    #     res = super(SaleOrder, self).action_confirm()
    #     # Code to send sms to customer of the order.
    #     sms_template_objs = self.env["wk.sms.template"].sudo().search(
    #         [('condition', '=', 'order_confirm'),('globally_access','=',False)])
    #
    #     if self.get_portal_last_transaction().acquirer_id.provider == 'cash_on_delivery' and self.state == 'sale':
    #         self.action_admin()
    #     for sms_template_obj in sms_template_objs:
    #         mobile = sms_template_obj._get_partner_mobile(self.partner_id)
    #         if mobile:
    #             sms_template_obj.send_sms_using_template(
    #                 mobile, sms_template_obj, obj=self)
    #     return res

    def action_admin(self):
        if self.filtered(lambda so: so.state != 'sale'):
            raise UserError(_('Only sale orders can be marked as sent directly.'))
        for order in self:
            order.message_subscribe(partner_ids=order.partner_id.ids)
        if self.write({'state': 'approve_by_admin'}):
            # Code to send sms to customer of the order.
            sms_template_objs = self.env["wk.sms.template"].sudo().search(
                [('condition', '=', 'order_confirm'),('globally_access','=',False)])
            for sms_template_obj in sms_template_objs:
                mobile = sms_template_obj._get_partner_mobile(self.partner_id)
                if mobile:
                    sms_template_obj.send_sms_using_template(
                        mobile, sms_template_obj, obj=self)
            # Code to send sms to customer of the order.
                
            picking_objs = self.env['stock.picking'].search([('origin','=',self.name)])
            delivery_vendor_obj = self.env['res.partner'].search([('delivery_vendor','=', True),('is_default','=', True)], limit=1)
            picking_vendor_obj = self.env['res.partner'].search([('picking_vendor','=', True),('is_default','=', True)], limit=1)
            
            delivery_vendor_obj.delivery_method_ids
            picking_vendor_obj.picking_method_ids
            
            for picking_data in picking_objs:
            
                seller_township = picking_data.marketplace_seller_id.township_id
                if not seller_township:
                    raise Warning("Township cannot be empty for seller %s" % picking_data.marketplace_seller_id.name)
                buyer_township = picking_data.partner_id.township_id
                if not buyer_township:
                    raise Warning("Township cannot be empty for buyer %s" % picking_data.partner_id.name)
                
                pick_all_zone = self.env['picking.method'].search([])
                pickup_zone = None
                delivery_zone = None
                pickup_person = None
                delivery_person = None
                
                for zone in picking_vendor_obj.picking_method_ids:
                    if seller_township in zone.township_ids:
                        pickup_zone = zone
                        
                        for pickup_person_data in picking_vendor_obj.child_ids:
                            if pickup_zone in pickup_person_data.picking_method_ids:
                                pickup_person = pickup_person_data.id
                        
                for d_zone in delivery_vendor_obj.delivery_method_ids:
                    if buyer_township in d_zone.township_ids:
                        delivery_zone = d_zone
                        
                        for delivery_person_data in delivery_vendor_obj.child_ids:
                            if delivery_zone in delivery_person_data.delivery_method_ids:
                                delivery_person = delivery_person_data.id
                                
                if not delivery_zone:
                    raise Warning("Need to setup delivery zone for buyer township %s" % buyer_township.name)
                if not pickup_zone:
                    raise Warning("Need to setup pickup zone for seller township %s" % seller_township.name)
                
                if picking_data.picking_type_id.name == 'Pick':
                    picking_data.write({'payment_provider': self.get_portal_last_transaction().acquirer_id.provider,
                                       'is_admin_approved': True,
                                       'vendor_id': picking_vendor_obj.id or None,
                                       'picking_method_id': pickup_zone.id or None,
                                       'pickup_person_id': pickup_person or None,
                                       'hold_state': False})
        
                    #if self.get_portal_last_transaction().acquirer_id.provider != 'cash_on_delivery':
                    #    picking_data.write({'payment_upload': self.payment_upload, 
                    #                       'paid_amount': self.get_portal_last_transaction().amount, 
                    #                       'payment_remark': self.get_portal_last_transaction().reference,                                   
                    #                       'journal_id': self.get_portal_last_transaction().acquirer_id.journal_id.id })
                        
                elif picking_data.picking_type_id.name == 'Pack':
                    picking_data.write({'payment_provider': self.get_portal_last_transaction().acquirer_id.provider,
                                       'is_admin_approved': True,
                                       'hold_state': False})
        
                    #if self.get_portal_last_transaction().acquirer_id.provider != 'cash_on_delivery':
                    #    picking_data.write({'payment_upload': self.payment_upload, 
                    #                       'paid_amount': self.get_portal_last_transaction().amount, 
                    #                       'payment_remark': self.get_portal_last_transaction().reference,                                   
                    #                       'journal_id': self.get_portal_last_transaction().acquirer_id.journal_id.id })
                
                elif picking_data.picking_type_id.name == 'Delivery Orders':
                        picking_data.write({'payment_provider': self.get_portal_last_transaction().acquirer_id.provider,
                                           'is_admin_approved': True,
                                           'vendor_id': delivery_vendor_obj.id or None,
                                           'delivery_method_id': delivery_zone.id or None,  
                                           'delivery_person_id': delivery_person or None,                                         
                                           'hold_state': False})
            
                        if self.get_portal_last_transaction().acquirer_id.provider != 'cash_on_delivery':
                            picking_data.write({'payment_upload': self.payment_upload, 
                                               'paid_amount': self.get_portal_last_transaction().amount, 
                                               'payment_remark': self.get_portal_last_transaction().reference,                                   
                                               'journal_id': self.get_portal_last_transaction().acquirer_id.journal_id.id })
                            
                        elif self.get_portal_last_transaction().acquirer_id.provider == 'cash_on_delivery':
                            picking_data.write({
                                               'paid_amount': self.get_portal_last_transaction().amount, 
                                               'payment_remark': self.get_portal_last_transaction().reference,                                   
                                               'journal_id': self.get_portal_last_transaction().acquirer_id.journal_id.id })
                
    

    # def action_cancel(self):
    #     res = super(SaleOrder, self).action_cancel()
    #     sms_template_objs = self.env["wk.sms.template"].sudo().search(
    #         [('condition', '=', 'order_cancel'),('globally_access','=',False)])
    #     for obj in self:

    #         for sms_template_obj in sms_template_objs:
    #             mobile = sms_template_obj._get_partner_mobile(obj.partner_id)
    #             if mobile:
    #                 sms_template_obj.send_sms_using_template(
    #                     mobile, sms_template_obj, obj=obj)
    #
    #     return res

    # def write(self, vals):
    #     result = super(SaleOrder, self).write(vals)
    #     for res in self:
    #         if res and vals.get("state", False) == 'sent':
    #             sms_template_objs = self.env["wk.sms.template"].sudo().search(
    #                 [('condition', '=', 'order_placed'),('globally_access','=',False)])
    #             for sms_template_obj in sms_template_objs:
    #                 mobile = sms_template_obj._get_partner_mobile(
    #                     res.partner_id)
    #                 if mobile:
    #                     sms_template_obj.send_sms_using_template(
    #                         mobile, sms_template_obj, obj=res)
    #     return result


class StockPicking(models.Model):
    _inherit = "stock.picking"

    # def write(self, vals):
    #     result = super(StockPicking, self).write(vals)
    #     for res in self:
    #         if res and vals.get("date_done", False):
    #             res.send_picking_done_message()
    #
    #     return result

    # method to send msg on picking done
    # def send_picking_done_message(self):
    #     sms_template_objs = self.env["wk.sms.template"].sudo().search(
    #         [('condition', '=', 'order_delivered'),('globally_access','=',False)])
    #     for sms_template_obj in sms_template_objs:
    #         mobile = sms_template_obj._get_partner_mobile(
    #             self.partner_id)
    #         if mobile:
    #             sms_template_obj.send_sms_using_template(
    #                 mobile, sms_template_obj, obj=self)


class AccountMove(models.Model):
    _inherit = "account.move"

    # def write(self, vals):
    #     result = super(AccountMove, self).write(vals)
    #     for res in self:
    #         if res and vals.get("state", False) in ["open", "paid"]:
    #             res.send_invoice_message(vals.get("state"))
    #     return result

    # method to send msg for open or paid invoice
    # def send_invoice_message(self,state):
    #     if state == 'open':
    #         sms_template_objs = self.env["wk.sms.template"].sudo().search(
    #             [('condition', '=', 'invoice_vaildate'),('globally_access','=',False)])
    #         for sms_template_obj in sms_template_objs:
    #             mobile = sms_template_obj._get_partner_mobile(
    #                 self.partner_id)
    #             if mobile:
    #                 sms_template_obj.send_sms_using_template(
    #                 mobile, sms_template_obj, obj=self)
    #     elif state == 'paid':
    #         sms_template_objs = self.env["wk.sms.template"].sudo().search(
    #             [('condition', '=', 'invoice_paid'),('globally_access','=',False)])
    #         for sms_template_obj in sms_template_objs:
    #             mobile = sms_template_obj._get_partner_mobile(
    #                 self.partner_id)
    #             if mobile:
    #                 sms_template_obj.send_sms_using_template(
    #                             mobile, sms_template_obj, obj=self)


class ProductProduct(models.Model):
    _inherit = "product.product"

    partner_id = fields.Many2one("res.partner", "Seller")

    def inventory_check(self):
        product_obj = self.env['product.product'].search([('active', '=', True)])
        for pobj in product_obj:
            quant_obj = self.env['stock.quant'].search([('product_id', '=', pobj.id), ('quantity', '>', 0), ('location_id', '=', 8)])
            for qobj in quant_obj:
                if qobj.quantity < 4:
                    self.send_inventory_warning_message(qobj.product_id.product_tmpl_id.marketplace_seller_id, pobj)


    # method to send msg to warn that inventory is almost empty
    def send_inventory_warning_message(self, partner_id, product_obj):
        sms_template_objs = self.env["wk.sms.template"].sudo().search(
            [('condition', '=', 'inventory_almost_empty'), ('globally_access', '=', False)])
        for sms_template_obj in sms_template_objs:
            mobile = sms_template_obj._get_partner_mobile(partner_id)
            if mobile:
                sms_template_obj.send_sms_using_template(
                    mobile, sms_template_obj, obj=product_obj)




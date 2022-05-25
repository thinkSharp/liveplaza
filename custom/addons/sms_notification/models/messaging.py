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
from odoo.http import request
from odoo.addons.auth_signup.models.res_partner import SignupError, now
from datetime import datetime, timedelta 

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


class ResUsers(models.Model):

    _inherit = "res.users"

    def reset_password_sms(self, login):
        """ retrieve the user corresponding to login (login or email),
            and reset their password
        """
        users = self.search([('login', '=', login)])
        if not users:
            users = self.search([('email', '=', login)])
        if len(users) != 1:
            raise Exception(_('Reset password: invalid username or email'))
        return users.action_reset_password_sms(login)
    
    def action_reset_password_sms(self, login):
        """ create signup token for each user, and send their signup url by email """
        # prepare reset password signup
        create_mode = bool(self.env.context.get('create_user'))

        # no time limit for initial invitation, only for reset password        
        reset_link_limit = datetime.now() + timedelta(hours=3)  #Fix reset password time limit for 3 hrs
        expiration = False if create_mode else reset_link_limit  #expiration = False if create_mode else now(days=+1)
        
        self.mapped('partner_id').signup_prepare(signup_type="reset", expiration=expiration)

        # send email to users with their signup url
        template = False
        if create_mode:
            try:
                template = self.env.ref('auth_signup.set_password_email', raise_if_not_found=False)
            except ValueError:
                pass
        if not template:
            template = self.env.ref('auth_signup.reset_password_email')
        assert template._name == 'mail.template'

        template_values = {
            'email_to': '${object.email|safe}',
            'email_cc': False,
            'auto_delete': True,
            'partner_to': False,
            'scheduled_date': False,
        }
        template.write(template_values)

        for user in self:
            if login.isdigit():
                self.sms_send_reset_password(login, False)
            else:
                if not user.email:
                    raise UserError(_("Cannot send email: user %s has no email address.") % user.name)
                with self.env.cr.savepoint():
                    force_send = not(self.env.context.get('import_file', False))
                    template.with_context(lang=user.lang).send_mail(user.id, force_send=force_send, raise_exception=True)
                _logger.info("Password reset email sent for user <%s> to <%s>", user.login, user.email)

    def action_reset_password(self):
        """ create signup token for each user, and send their signup url by email """
        # prepare reset password signup
        create_mode = bool(self.env.context.get('create_user'))

        # no time limit for initial invitation, only for reset password
        reset_link_limit = datetime.now() + timedelta(hours=3)  #Fix reset password time limit for 3 hrs
        expiration = False if create_mode else reset_link_limit  #expiration = False if create_mode else now(days=+1)

        self.mapped('partner_id').signup_prepare(signup_type="reset", expiration=expiration)

        # send email to users with their signup url
        template = False
        if create_mode:
            try:
                template = self.env.ref('auth_signup.set_password_email', raise_if_not_found=False)
            except ValueError:
                pass
        if not template:
            template = self.env.ref('auth_signup.reset_password_email')
        assert template._name == 'mail.template'

        template_values = {
            'email_to': '${object.email|safe}',
            'email_cc': False,
            'auto_delete': True,
            'partner_to': False,
            'scheduled_date': False,
        }
        template.write(template_values)

        for user in self:
            if not user.email:
                raise UserError(_("Cannot send email: user %s has no email address.") % user.name)
            with self.env.cr.savepoint():
                force_send = not(self.env.context.get('import_file', False))
                template.with_context(lang=user.lang).send_mail(user.id, force_send=force_send, raise_exception=True)
            _logger.info("Password reset email sent for user <%s> to <%s>", user.login, user.email)
            
    def sms_send_reset_password(self, mobile, phone_code):
        otp_notification_mode = self.env['ir.default'].sudo().get(
            'website.otp.settings', 'otp_notification_mode')
        userObj = self.env["res.users"].sudo().search([("login", "=", mobile)], limit=1)
        userName = userObj.name
        if otp_notification_mode != 'email':
            try:
                if not userObj:
                    userObj = self.env["res.users"].sudo().search(
                        [("mobile", "=", mobile)], limit=1)
                    userName = userObj.name
                sms_template_objs = self.env["wk.sms.template"].sudo().search(
                    [('condition', '=', 'reset_password'), ('globally_access', '=', False)])
                if mobile:
                    for sms_template_obj in sms_template_objs:
                        ctx = dict(sms_template_obj._context or {})
                        ctx['name'] = userName or 'User'
                        if phone_code:
                            if mobile[:1] == '0':
                                mobile = "+{}{}".format(phone_code, mobile[1:])
                            elif "+" not in mobile:
                                mobile = "+{}{}".format(phone_code, mobile)
                        (sms_template_obj, (ctx))

                        sms_template_obj.with_context(ctx).send_sms_using_template(
                            mobile, sms_template_obj, obj=userObj)
                        
            except Exception as e:
                _logger.info("---Exception raised : %r while sending reset password confirmation", e)

        return self
      
class ResPartner(models.Model):
    _inherit = "res.partner"

    inventory_empty_product = fields.Text(string='Inventory Empty Product')

    def inventory_check(self):
        smsList = []
        seller_obj = self.env['res.partner'].search([('seller', '=', True), ('active', '=', True)])
        self.min_qty = self.env['ir.default'].get('res.config.settings', 'min_qty_for_sms_warning')

        for sobj in seller_obj:
            product_tmpl_obj = self.env['product.template'].search([('marketplace_seller_id', '=', sobj.id)])
            p_tmpl_list = []

            for p_tmpl_obj in product_tmpl_obj:
                p_tmpl_list.append(p_tmpl_obj.id)

            product_obj = self.env['product.product'].search([('active', '=', True), ('product_tmpl_id', 'in', p_tmpl_list)])

            for pobj in product_obj:
                quant_obj = self.env['stock.quant'].search([('product_id', '=', pobj.id), ('quantity', '>', 0), ('location_id', '=', 8)])
                for qobj in quant_obj:
                    if qobj.quantity < self.min_qty:
                        qdict = {"seller_id": sobj, "product_id": pobj}
                        smsList.append(qdict)

        sms_seller = []
        for smslist in smsList:
            seller_id = smslist.get('seller_id')
            if seller_id not in sms_seller:
                sms_seller.append(seller_id)

        for s_obj in sms_seller:
            sms_product = []
            sms_product_msg = 'Almost Out of Stock Product(s): '

            for sms_list in smsList:
                if sms_list.get('seller_id').id == s_obj.id:
                    sms_product.append(sms_list.get('product_id'))

            for sms_p in sms_product:
                sms_product_msg += sms_p.name + ':' + ' ' + str(sms_p.qty_available) + ' ' + '|' + ' '
            s_obj.write({'inventory_empty_product':sms_product_msg})
            self.send_inventory_warning_message(s_obj, s_obj)


    # method to send msg to warn that inventory is almost empty
    def send_inventory_warning_message(self, partner_id, seller_obj):
        sms_template_objs = self.env["wk.sms.template"].sudo().search(
            [('condition', '=', 'inventory_almost_empty'), ('globally_access', '=', False)])
        for sms_template_obj in sms_template_objs:
            mobile = sms_template_obj._get_partner_mobile(partner_id)
            if mobile:
                sms_template_obj.send_sms_using_template(
                    mobile, sms_template_obj, obj=seller_obj)




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

import logging
import re
from os.path import isdir

from html.parser import HTMLParser
from odoo import _, api, fields, models, tools

_logger = logging.getLogger(__name__)

from .utils import parse_subscriber_number_mm


# http://stackoverflow.com/questions/38200739/extract-text-from-html-mail-odoo
class MLStripper(HTMLParser):
    def __init__(self):
        super().__init__()
        self.reset()
        self.fed = []

    def handle_data(self, d):
        self.fed.append(d)

    def get_data(self):
        return ''.join(self.fed)


def strip_tags(html):
    s = MLStripper()
    s.feed(html)
    return s.get_data()


class SmsTemplate(models.Model):
    "Templates for sending sms"
    _name = "wk.sms.template"
    _description = 'SMS Templates'
    _order = 'name'

    active = fields.Boolean(string="Active", default=True)
    name = fields.Char('Name', required=True)
    auto_delete = fields.Boolean("Auto Delete")
    globally_access = fields.Boolean(
        string="Global",
        help="if enable then it will consider normal(global) template.You can use it while sending the bulk message. If not enable the you have to select condition on which the template applies.")
    condition = fields.Selection([('order_placed', 'Order Placed'),
                                  ('order_confirm', 'Order Confirmed'),
                                  ('reset_password', 'Reset Password'),
                                  ('order_delivered', 'Order Delivered'),
                                  ('invoice_vaildate', 'Invoice Validate'),
                                  ('invoice_paid', 'Invoice Paid'),
                                  ('order_cancel', 'Order Cancelled'),
                                  ('inventory_almost_empty', 'Inventory Almost Empty'),
                                  ('ticket_ready', 'Ticket Ready'),
                                  ('booking_ticket_ready', 'Booking Ticket Ready'),
                                  ('sale_order_line_cancel', 'Sale Order Line Cancel'),
                                  ('final_sale_order_line_cancel', 'Final Sale Order Line Cancel')],
                                  string="Conditions",
                                 help="Condition on which the template has been applied.")
    model_id = fields.Many2one(
        'ir.model', 'Applies to', compute="onchange_condition",
        help="The kind of document with this template can be used. Note if not selected then it will consider normal(global) template.",
        store=True)
    model = fields.Char(related="model_id.model", string='Related Document Model',
                        store=True, readonly=True)
    sms_body_html = fields.Text('Body', translate=True, sanitize=False,
                                help="SMS text. You can also use ${object.partner_id} for dynamic text. Here partner_id is a field of the document(obj/model).")
    lang = fields.Char('Language', help="Use this field to either force a specific language (ISO code) or dynamically "
                                        "detect the language of your recipient by a placeholder expression "
                                        "(e.g. ${object.partner_id.lang})")

    def _get_partner_mobile(self, partner):
        mobile = partner.mobile if partner.mobile else partner.phone
        if not mobile:
            return False
        company_country_calling_code = self.env.user.company_id.country_id.phone_code
        managed_calling_code = self.env['ir.config_parameter'].get_param(
            'sms_notification.is_phone_code_enable', 'False') == 'True'
        if managed_calling_code:
            return mobile
        if partner.country_id and partner.country_id.phone_code:
            country_calling_code = partner.country_id.phone_code
        else:
            country_calling_code = company_country_calling_code
        subscriber_number = parse_subscriber_number_mm(mobile)
        return "+{code}{subscriber_number}".format(code=country_calling_code, subscriber_number=subscriber_number)

    @api.depends('condition')
    def onchange_condition(self):
        for obj in self:
            if obj.condition:
                if obj.condition in ['order_placed', 'order_confirm', 'order_cancel']:
                    model_id = self.env['ir.model'].search(
                        [('model', '=', 'sale.order')])
                    obj.model_id = model_id.id if model_id else False
                    obj.lang = '${object.partner_id.lang}'
                elif obj.condition in ['order_delivered']:
                    model_id = self.env['ir.model'].search(
                        [('model', '=', 'stock.picking')])
                    obj.model_id = model_id.id if model_id else False
                    obj.lang = '${object.partner_id.lang}'
                elif obj.condition in ['ticket_ready']:
                    model_id = self.env['ir.model'].search(
                        [('model', '=', 'ticket')])
                    obj.model_id = model_id.id if model_id else False
                    obj.lang = '${object.sale_order.partner_id.lang}'

                elif obj.condition in ['booking_ticket_ready']:
                    model_id = self.env['ir.model'].search(
                        [('model', '=', 'booking.ticket')])
                    obj.model_id = model_id.id if model_id else False
                    obj.lang = '${object.sale_order.partner_id.lang}'

                elif obj.condition in ['sale_order_line_cancel', 'final_sale_order_line_cancel']:
                    model_id = self.env['ir.model'].search(
                        [('model', '=', 'sale.order.line')])
                    obj.model_id = model_id.id if model_id else False
                    obj.lang = '${object.order_id.partner_id.lang}'

                elif obj.condition in ['invoice_vaildate', 'invoice_paid']:
                    model_id = self.env['ir.model'].search(
                        [('model', '=', 'account.move')])
                    obj.model_id = model_id.id if model_id else False
                    obj.lang = '${object.partner_id.lang}'
                elif obj.condition in ['reset_password']:
                    model_id = self.env['ir.model'].search(
                        [('model', '=', 'res.users')])
                    obj.model_id = model_id.id if model_id else False
                    obj.lang = '${object.partner_id.lang}'
                elif obj.condition in ['inventory_almost_empty']:
                    model_id = self.env['ir.model'].search(
                        [('model', '=', 'res.partner')])
                    obj.model_id = model_id.id if model_id else False
                    obj.lang = 'en_US'
            else:
                obj.model_id = False
                obj.lang = False

    @api.onchange('model_id')
    def onchange_model_id(self):
        if self.model_id:
            self.model = self.model_id.model
        else:
            self.model = False

    def _get_context_lang_per_id(self, res_ids):
        self.ensure_one()
        if res_ids is None:
            return {None: self}

        if self.env.context.get('template_preview_lang'):
            lang = self.env.context.get('template_preview_lang')
            results = dict((res_id, self.with_context(lang=lang)) for res_id in res_ids)
        else:
            rendered_langs = self._render_template(self.lang, self.model, res_ids)
            results = dict((res_id, self.with_context(lang=lang) if lang else self)
                           for res_id, lang in rendered_langs.items())

        return results

    def _get_ids_per_lang(self, res_ids):
        self.ensure_one()
        rids_to_tpl = self._get_context_lang_per_id(res_ids)
        tpl_to_rids = {}
        for res_id, template in rids_to_tpl.items():
            tpl_to_rids.setdefault(template._context.get('lang', self.env.user.lang), []).append(res_id)

        return tpl_to_rids

    def get_body_data(self, obj, partner_id=None):
        self.ensure_one()
        lang_to_rids = self._get_ids_per_lang(obj.ids)
        all_bodies = {}
        for lang, rids in lang_to_rids.items():
            template = self.with_context(lang=lang)
            all_bodies.update(template._render_template(template.sms_body_html, self.model, rids))
        return all_bodies.get(obj.id)

    @api.model
    def _render_template(self, template_txt, model, res_ids):
        """ Render the jinja template """
        return self.env['mail.template']._render_template(template_txt, model, res_ids)

    @api.model
    def send_sms_using_template(self, mob_no, sms_tmpl, sms_gateway=None, obj=None):
        if not sms_gateway:
            gateway_id = self.env["sms.mail.server"].search(
                [], order='sequence asc', limit=1)
        else:
            gateway_id = sms_gateway
        if mob_no and sms_tmpl:
            ctx = dict(self._context or {})
            uid = self.sudo()._uid
            if sms_tmpl.condition == 'order_confirm':
                sms_sms_obj = self.env["wk.sms.sms"].create({
                    'sms_gateway_config_id': gateway_id.id,
                    'partner_id': obj.partner_id.id if obj else False,
                    'to': mob_no,
                    'group_type': 'individual',
                    'auto_delete': sms_tmpl.auto_delete,
                    'msg': sms_tmpl.with_context(ctx).get_body_data(obj,
                                                                    obj.partner_id) if obj else sms_tmpl.sms_body_html,
                    'template_id': False
                })
                if sms_sms_obj.msg:
                    url_msg = sms_sms_obj.msg.replace("&amp;", "&")
                    sms_sms_obj.sudo().write({'msg': url_msg})

            elif sms_tmpl.condition == 'order_cancel':
                sms_sms_obj = self.env["wk.sms.sms"].create({
                    'sms_gateway_config_id': gateway_id.id,
                    'partner_id': obj.partner_id.id if obj else False,
                    'to': mob_no,
                    'group_type': 'individual',
                    'auto_delete': sms_tmpl.auto_delete,
                    'msg': sms_tmpl.with_context(ctx).get_body_data(obj,
                                                                    obj.partner_id) if obj else sms_tmpl.sms_body_html,
                    'template_id': False
                })

            elif sms_tmpl.condition == 'ticket_ready':
                print("Obj Print............", obj)
                print("partner", obj.sale_order.partner_id)
                sms_sms_obj = self.env["wk.sms.sms"].create({
                    'sms_gateway_config_id': gateway_id.id,
                    'partner_id': obj.sale_order.partner_id.id if obj else False,
                    'to': mob_no,
                    'group_type': 'individual',
                    'auto_delete': sms_tmpl.auto_delete,
                    'msg': sms_tmpl.with_context(ctx).get_body_data(obj,
                                                                    obj.sale_order.partner_id) if obj else sms_tmpl.sms_body_html,
                    'template_id': False
                })

            elif sms_tmpl.condition == 'booking_ticket_ready':
                print("Obj Print............", obj)
                print("partner", obj.sale_order.partner_id)
                sms_sms_obj = self.env["wk.sms.sms"].create({
                    'sms_gateway_config_id': gateway_id.id,
                    'partner_id': obj.sale_order.partner_id.id if obj else False,
                    'to': mob_no,
                    'group_type': 'individual',
                    'auto_delete': sms_tmpl.auto_delete,
                    'msg': sms_tmpl.with_context(ctx).get_body_data(obj,
                                                                    obj.sale_order.partner_id) if obj else sms_tmpl.sms_body_html,
                    'template_id': False
                })

            elif sms_tmpl.condition in ['sale_order_line_cancel', 'final_sale_order_line_cancel']:
                sms_sms_obj = self.env["wk.sms.sms"].create({
                    'sms_gateway_config_id': gateway_id.id,
                    'partner_id': obj.order_id.partner_id.id  if obj else False,
                    'to': mob_no,
                    'group_type': 'individual',
                    'auto_delete': sms_tmpl.auto_delete,
                    'msg': sms_tmpl.with_context(ctx).get_body_data(obj,
                                                                    obj.order_id.partner_id) if obj else sms_tmpl.sms_body_html,
                    'template_id': False
                })

            elif sms_tmpl.condition == 'reset_password':
                sms_sms_obj = self.env["wk.sms.sms"].create({
                    'sms_gateway_config_id': gateway_id.id,
                    'partner_id': obj.partner_id.id if obj else False,
                    'to': mob_no,
                    'group_type': 'individual',
                    'auto_delete': sms_tmpl.auto_delete,
                    'msg': sms_tmpl.with_context(ctx).get_body_data(obj,
                                                                    obj.partner_id) if obj else sms_tmpl.sms_body_html,
                })


                if sms_sms_obj.msg:
                    url_msg = sms_sms_obj.msg.replace("&amp;", "&")
                    sms_sms_obj.sudo().write({'msg': url_msg})

            elif sms_tmpl.condition == 'inventory_almost_empty':
                sms_sms_obj = self.env["wk.sms.sms"].create({
                    'sms_gateway_config_id': gateway_id.id,
                    'partner_id': obj.id if obj else False,
                    'to': mob_no,
                    'group_type': 'individual',
                    'auto_delete': sms_tmpl.auto_delete,
                    'msg': sms_tmpl.with_context(ctx).get_body_data(obj, obj) if obj else sms_tmpl.sms_body_html,
                    'template_id': False
                })
            else:
                sms_sms_obj = self.env["wk.sms.sms"].create({
                    'sms_gateway_config_id': gateway_id.id,
                    'partner_id': obj.partner_id.id if obj else False,
                    'to': mob_no,
                    'group_type': 'individual',
                    'auto_delete': sms_tmpl.auto_delete,
                    'msg': sms_tmpl.with_context(ctx).get_body_data(sms_tmpl, uid) or sms_tmpl.sms_body_html,
                    'template_id': False
                })
            return sms_sms_obj.send_sms_via_gateway(
                sms_sms_obj.msg, [sms_sms_obj.to], from_mob=None, sms_gateway=gateway_id)
        return False
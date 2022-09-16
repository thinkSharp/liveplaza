# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import binascii
from datetime import date

from odoo import fields, http, _
from odoo.exceptions import AccessError, MissingError
from odoo.http import request
from odoo.addons.payment.controllers.portal import PaymentProcessing
from odoo.addons.portal.controllers.mail import _message_post_helper
from odoo.addons.portal.controllers.portal import CustomerPortal, pager as portal_pager, get_records_pager
from odoo.osv import expression
from datetime import datetime
import datetime
import pytz
import base64


class CustomerPortal(CustomerPortal):

    def _prepare_home_portal_values(self):
        values = super(CustomerPortal, self)._prepare_home_portal_values()
        partner = request.env.user.partner_id

        SaleOrder = request.env['sale.order']
        quotation_count = SaleOrder.search_count([
            ('message_partner_ids', 'child_of', [partner.commercial_partner_id.id]),
            ('state', 'in', ['draft', 'sent'])
        ])
        order_count = SaleOrder.search_count([
            ('message_partner_ids', 'child_of', [partner.commercial_partner_id.id]),
            ('state', 'in', ['approve_by_admin', 'ready_to_pick', 'sale', 'done'])
        ])

        cancel_order_count = SaleOrder.search_count([
            ('message_partner_ids', 'child_of', [partner.commercial_partner_id.id]),
            ('state', '=', 'cancel')
        ])

        values.update({
            'quotation_count': quotation_count,
            'order_count': order_count,
            'cancel_order_count': cancel_order_count
        })
        return values

    @http.route(['/my/orders', '/my/orders/page/<int:page>'], type='http', auth="user", website=True)
    def portal_my_orders(self, page=1, date_begin=None, date_end=None, sortby=None, **kw):
        values = self._prepare_portal_layout_values()
        partner = request.env.user.partner_id
        SaleOrder = request.env['sale.order']

        domain = [
            ('message_partner_ids', 'child_of', [partner.commercial_partner_id.id]),
            ('state', 'in', ['approve_by_admin', 'ready_to_pick', 'sale', 'done'])
        ]

        searchbar_sortings = {
            'date': {'label': _('Order Date'), 'order': 'date_order desc'},
            'name': {'label': _('Reference'), 'order': 'name'},
            'stage': {'label': _('Stage'), 'order': 'state'},
        }
        # default sortby order
        if not sortby:
            sortby = 'date'
        sort_order = searchbar_sortings[sortby]['order']

        archive_groups = self._get_archive_groups('sale.order', domain) if values.get('my_details') else []
        if date_begin and date_end:
            domain += [('create_date', '>', date_begin), ('create_date', '<=', date_end)]

        # count for pager
        order_count = SaleOrder.search_count(domain)
        # pager
        pager = portal_pager(
            url="/my/orders",
            url_args={'date_begin': date_begin, 'date_end': date_end, 'sortby': sortby},
            total=order_count,
            page=page,
            step=self._items_per_page
        )
        # content according to pager and archive selected
        orders = SaleOrder.search(domain, order=sort_order, limit=self._items_per_page, offset=pager['offset'])
        request.session['my_orders_history'] = orders.ids[:100]

        order_lines = []
        product_ids = []
        for o in orders:
            for line in o.order_line:
                if line.product_id not in product_ids:
                    order_lines.append(line)
                product_ids.append(line.product_id)

        values.update({
            'date': date_begin,
            'orders': orders.sudo(),
            'page_name': 'order',
            'pager': pager,
            'archive_groups': archive_groups,
            'default_url': '/my/orders',
            'searchbar_sortings': searchbar_sortings,
            'sortby': sortby,
            'order_lines': order_lines,
        })
        return request.render("do_customization.portal_my_orders_new", values)

    @http.route(['/my/cancel_orders', '/my/cancel_orders/page/<int:page>'], type='http', auth="user", website=True)
    def portal_my_cancel_orders(self, page=1, date_begin=None, date_end=None, sortby=None, **kw):
        values = self._prepare_portal_layout_values()
        partner = request.env.user.partner_id
        SaleOrder = request.env['sale.order']

        domain = [
            ('message_partner_ids', 'child_of', [partner.commercial_partner_id.id]),
            ('state', '=', 'cancel')
        ]

        searchbar_sortings = {
            'date': {'label': _('Order Date'), 'order': 'date_order desc'},
            'name': {'label': _('Reference'), 'order': 'name'},
            'stage': {'label': _('Stage'), 'order': 'state'},
        }
        # default sortby order
        if not sortby:
            sortby = 'date'
        sort_order = searchbar_sortings[sortby]['order']

        archive_groups = self._get_archive_groups('sale.order', domain) if values.get('my_details') else []
        if date_begin and date_end:
            domain += [('create_date', '>', date_begin), ('create_date', '<=', date_end)]

        # count for pager
        order_count = SaleOrder.search_count(domain)
        # pager
        pager = portal_pager(
            url="/my/cancel_orders",
            url_args={'date_begin': date_begin, 'date_end': date_end, 'sortby': sortby},
            total=order_count,
            page=page,
            step=self._items_per_page
        )
        # content according to pager and archive selected
        orders = SaleOrder.search(domain, order=sort_order, limit=self._items_per_page, offset=pager['offset'])
        request.session['my_orders_history'] = orders.ids[:100]

        order_lines = []
        product_ids = []
        for o in orders:
            for line in o.order_line:
                if line.product_id not in product_ids:
                    order_lines.append(line)
                product_ids.append(line.product_id)

        values.update({
            'date': date_begin,
            'orders': orders.sudo(),
            'page_name': 'cancel_order',
            'pager': pager,
            'archive_groups': archive_groups,
            'default_url': '/my/cancel_orders',
            'searchbar_sortings': searchbar_sortings,
            'sortby': sortby,
            'order_lines': order_lines,
            'cancel': True,
        })
        return request.render("do_customization.portal_my_cancel_orders", values)

    @http.route(['/my/cancel_orders/<int:order_id>'], type='http', auth="public", website=True)
    def portal_cancel_order_page(self, order_id, report_type=None, access_token=None, message=False, download=False, **kw):
        try:
            order_sudo = self._document_check_access('sale.order', order_id, access_token=access_token)
        except (AccessError, MissingError):
            return request.redirect('/my')

        if report_type in ('html', 'pdf', 'text'):
            return self._show_report(model=order_sudo, report_type=report_type,
                                     report_ref='sale.action_report_saleorder', download=download)

        # use sudo to allow accessing/viewing orders for public user
        # only if he knows the private token
        # Log only once a day
        if order_sudo:
            now = fields.Date.today().isoformat()
            session_obj_date = request.session.get('view_quote_%s' % order_sudo.id)
            if isinstance(session_obj_date, date):
                session_obj_date = session_obj_date.isoformat()
            if session_obj_date != now and request.env.user.share and access_token:
                request.session['view_quote_%s' % order_sudo.id] = now
                body = _('Quotation viewed by customer %s') % order_sudo.partner_id.name
                _message_post_helper(
                    "sale.order",
                    order_sudo.id,
                    body,
                    token=order_sudo.access_token,
                    message_type="notification",
                    subtype="mail.mt_note",
                    partner_ids=order_sudo.user_id.sudo().partner_id.ids,
                )

            picking = request.env["stock.picking"].search([('origin', '=', order_sudo.name)])

        delivery_progress = self.get_order_delivery_progress(order_sudo)

        values = {
            'picking': picking,
            'cancel_order': order_sudo,
            'sale_order': None,
            'delivery_progress': delivery_progress,
            'message': message,
            'token': access_token,
            'return_url': '/shop/payment/validate',
            'bootstrap_formatting': True,
            'partner_id': order_sudo.partner_id.id,
            'report_type': 'html',
            'action': order_sudo._get_portal_return_action(),
            'cancel': True,
        }
        if order_sudo.company_id:
            values['res_company'] = order_sudo.company_id

        if order_sudo.has_to_be_paid():
            domain = expression.AND([
                ['&', ('state', 'in', ['enabled', 'test']), ('company_id', '=', order_sudo.company_id.id)],
                ['|', ('country_ids', '=', False), ('country_ids', 'in', [order_sudo.partner_id.country_id.id])]
            ])
            acquirers = request.env['payment.acquirer'].sudo().search(domain)

            values['acquirers'] = acquirers.filtered(
                lambda acq: (acq.payment_flow == 'form' and acq.view_template_id) or
                            (acq.payment_flow == 's2s' and acq.registration_view_template_id))
            values['pms'] = request.env['payment.token'].search([('partner_id', '=', order_sudo.partner_id.id)])
            values['acq_extra_fees'] = acquirers.get_acquirer_extra_fees(order_sudo.amount_total,
                                                                         order_sudo.currency_id,
                                                                         order_sudo.partner_id.country_id.id)

        if order_sudo.state in ('draft', 'sent', 'cancel'):
            history = request.session.get('my_quotations_history', [])
        else:
            history = request.session.get('my_orders_history', [])
        values.update(get_records_pager(history, order_sudo))

        return request.render('do_customization.order_details_page', values)

    @http.route(['/my/orders/<int:order_id>'], type='http', auth="public", website=True)
    def portal_order_page(self, order_id, report_type=None, access_token=None, message=False, download=False, **kw):
        try:
            order_sudo = self._document_check_access('sale.order', order_id, access_token=access_token)
        except (AccessError, MissingError):
            return request.redirect('/my')

        if report_type in ('html', 'pdf', 'text'):
            return self._show_report(model=order_sudo, report_type=report_type,
                                     report_ref='sale.action_report_saleorder', download=download)

        # use sudo to allow accessing/viewing orders for public user
        # only if he knows the private token
        # Log only once a day
        if order_sudo:
            now = fields.Date.today().isoformat()
            session_obj_date = request.session.get('view_quote_%s' % order_sudo.id)
            if isinstance(session_obj_date, date):
                session_obj_date = session_obj_date.isoformat()
            if session_obj_date != now and request.env.user.share and access_token:
                request.session['view_quote_%s' % order_sudo.id] = now
                body = _('Quotation viewed by customer %s') % order_sudo.partner_id.name
                _message_post_helper(
                    "sale.order",
                    order_sudo.id,
                    body,
                    token=order_sudo.access_token,
                    message_type="notification",
                    subtype="mail.mt_note",
                    partner_ids=order_sudo.user_id.sudo().partner_id.ids,
                )

            picking = request.env["stock.picking"].search([('origin', '=', order_sudo.name)])

        delivery_progress = self.get_order_delivery_progress(order_sudo)

        values = {
            'picking': picking,
            'sale_order': order_sudo,
            'delivery_progress': delivery_progress,
            'message': message,
            'token': access_token,
            'return_url': '/shop/payment/validate',
            'bootstrap_formatting': True,
            'partner_id': order_sudo.partner_id.id,
            'report_type': 'html',
            'action': order_sudo._get_portal_return_action(),
            'track_product': True,
        }
        if order_sudo.company_id:
            values['res_company'] = order_sudo.company_id

        if order_sudo.has_to_be_paid():
            domain = expression.AND([
                ['&', ('state', 'in', ['enabled', 'test']), ('company_id', '=', order_sudo.company_id.id)],
                ['|', ('country_ids', '=', False), ('country_ids', 'in', [order_sudo.partner_id.country_id.id])]
            ])
            acquirers = request.env['payment.acquirer'].sudo().search(domain)

            values['acquirers'] = acquirers.filtered(
                lambda acq: (acq.payment_flow == 'form' and acq.view_template_id) or
                            (acq.payment_flow == 's2s' and acq.registration_view_template_id))
            values['pms'] = request.env['payment.token'].search([('partner_id', '=', order_sudo.partner_id.id)])
            values['acq_extra_fees'] = acquirers.get_acquirer_extra_fees(order_sudo.amount_total,
                                                                         order_sudo.currency_id,
                                                                         order_sudo.partner_id.country_id.id)

        if order_sudo.state in ('draft', 'sent', 'cancel'):
            history = request.session.get('my_quotations_history', [])
        else:
            history = request.session.get('my_orders_history', [])
        values.update(get_records_pager(history, order_sudo))

        return request.render('do_customization.order_details_page', values)

    @http.route(['/orders/order_line/delivery_tracking/modal'], type='json', auth="public", methods=['POST'], website=True)
    def order_line_delivery_tracking_modal(self, line_id):
        order_line = request.env['sale.order.line'].search([('id', '=', line_id)])
        delivery_progress = order_line.get_sol_delivery_progress()
        values = {
            'delivery_progress': delivery_progress,
            'line': order_line,
        }
        return request.env.ref("do_customization.product_delivery_tracking").render(values, engine='ir.qweb')

    def change_datetime_format(self, d):
        if d:
            tz = d.astimezone(pytz.timezone('Asia/Yangon'))
            return tz.strftime("%d %b %Y - %H:%M")
        else:
            return ""

    def check_service_order(self, order):
        for line in order.order_line:
            if not (line.product_id.is_service or line.product_id.is_booking_type):
                return False
        return True

    def get_order_delivery_progress(self, order):
        create_date = self.change_datetime_format(order.create_date)
        picking_date = self.change_datetime_format(order.picking_date)
        packing_date = self.change_datetime_format(order.packing_date)
        delivering_date = self.change_datetime_format(order.delivering_date)
        delivered_date = self.change_datetime_format(order.delivered_date)
        delivery_state = []
        delivery_completion = []

        # for products
        if self.check_service_order(order):
            delivery_status = {'delivered': 'complete', 'ordered': 'complete'}
            if order.state in ('approve_by_admin', 'ready_to_pick'):
                order.service_delivery_status = 'delivered'
            status = order.service_delivery_status
        else:
            delivery_status = {'delivered': "complete", 'delivering': 'complete', 'packed': 'complete', 'picked': 'complete',
                          'ordered': 'complete'}
            status = order.delivery_status

        for s, p in delivery_status.items():
            if s == status:
                if s == 'delivering':
                    delivery_status[s] = 'current'
                break
            else:
                delivery_status[s] = 'not_yet'

        for s, p in delivery_status.items():
            delivery_state.append(s)
            delivery_completion.append(p)

        delivery_state.reverse()
        delivery_completion.reverse()

        delivery_progress = {state: {} for state in delivery_state}
        delivery_dates = [create_date, picking_date, packing_date,
                          delivering_date, delivered_date]

        for i in range(len(delivery_state)):
            delivery_progress[delivery_state[i]] = [delivery_completion[i], delivery_dates[i]]

        return delivery_progress

    @http.route(['/my/quotes', '/my/quotes/page/<int:page>'], type='http', auth="user", website=True)
    def portal_my_quotes(self, page=1, date_begin=None, date_end=None, sortby=None, **kw):
        values = self._prepare_portal_layout_values()
        partner = request.env.user.partner_id
        SaleOrder = request.env['sale.order']

        domain = [
            ('message_partner_ids', 'child_of', [partner.commercial_partner_id.id]),
            ('state', 'in', ['draft', 'sent'])
        ]

        searchbar_sortings = {
            'date': {'label': _('Order Date'), 'order': 'date_order desc'},
            'name': {'label': _('Reference'), 'order': 'name'},
            'stage': {'label': _('Stage'), 'order': 'state'},
        }

        # default sortby order
        if not sortby:
            sortby = 'date'
        sort_order = searchbar_sortings[sortby]['order']

        archive_groups = self._get_archive_groups('sale.order', domain) if values.get('my_details') else []
        if date_begin and date_end:
            domain += [('create_date', '>', date_begin), ('create_date', '<=', date_end)]

        # count for pager
        quotation_count = SaleOrder.search_count(domain)
        # make pager
        pager = portal_pager(
            url="/my/quotes",
            url_args={'date_begin': date_begin, 'date_end': date_end, 'sortby': sortby},
            total=quotation_count,
            page=page,
            step=self._items_per_page
        )
        # search the count to display, according to the pager data
        quotations = SaleOrder.search(domain, order=sort_order, limit=self._items_per_page, offset=pager['offset'])
        request.session['my_quotations_history'] = quotations.ids[:100]

        values.update({
            'date': date_begin,
            'quotations': quotations.sudo(),
            'page_name': 'quote',
            'pager': pager,
            'archive_groups': archive_groups,
            'default_url': '/my/quotes',
            'searchbar_sortings': searchbar_sortings,
            'sortby': sortby,
        })
        return request.render("sale.portal_my_quotations", values)

    @http.route(['/my/orders/payment/edit_modal'], type='json', auth="public", methods=['POST'], website=True)
    def edit_payment_ss(self, sale_order_id):
        order = request.env['sale.order'].search([('id', '=', sale_order_id)])
        values = {
            'order': order,
        }
        return request.env.ref("do_customization.payment_ss_update").render(values, engine='ir.qweb')

    @http.route(['/my/orders/payment/view_modal'], type='json', auth="public", methods=['POST'], website=True)
    def view_payment_ss(self, sale_order_id):
        order = request.env['sale.order'].search([('id', '=', sale_order_id)])
        values = {
            'order': order,
        }
        return request.env.ref("do_customization.payment_ss_view_modal").render(values, engine='ir.qweb')

    @http.route('/my/orders/payment/edit', type='http', auth="public", website=True)
    def upload_payment_ss(self, **post):
        values = {}

        if post.get('attachment', False):
            name = post.get('attachment').filename
            if name and name.lower().endswith(('.png', '.jpeg', '.gif', 'jpg', 'tiff', 'raw')):
                file = post.get('attachment')
                sale_order_id = post.get('sale_order_id')
                attachment = file.read()
                image_64_encode = base64.encodestring(attachment)
                # image_64_decode = base64.decodestring(image_64_encode)
                order = request.env['sale.order'].sudo().browse(sale_order_id).exists()
                sale_order_objs = request.env['sale.order'].sudo().search([("id", "=", int(sale_order_id))])

                if sale_order_objs:
                    for sale_order_obj in sale_order_objs:
                        sale_order_obj.sudo().write({'payment_upload': image_64_encode, 'payment_upload_name': name})

                values = {
                    'website_sale_order': order,
                    'order': order,
                }
                url = sale_order_objs.get_portal_url()
                return request.redirect(url)
            else:
                return request.redirect('/shop/confirmation')



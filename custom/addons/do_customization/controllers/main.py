import werkzeug
import odoo
from odoo.addons.auth_signup.models.res_users import SignupError
from odoo.addons.web.controllers.main import ensure_db
from odoo import http, tools
from odoo.http import request
# from odoo.addons.web.controllers.main import binary_content
import base64
from odoo.tools.translate import _
from odoo import SUPERUSER_ID
from odoo.addons.website_sale.controllers.main import TableCompute, QueryURL, WebsiteSale
from odoo.addons.auth_signup.controllers.main import AuthSignupHome
from odoo.addons.website_mail.controllers.main import WebsiteMail
from odoo.addons.website.controllers.main import Website
from odoo.addons.portal.controllers.web import Home
from odoo.exceptions import UserError, ValidationError
from odoo.osv import expression
from odoo.tools.misc import formatLang, format_date, get_lang
from odoo.addons.payment.controllers.portal import PaymentProcessing

import logging
_logger = logging.getLogger(__name__)
import urllib.parse as urlparse
import re
from urllib.parse import urlencode


PPG = 20  # Products Per Page
PPR = 4   # Products Per Row

SPG = 20  # Shops/sellers Per Page
SPR = 4   # Shops/sellers Per Row


marketplace_domain = [('sale_ok', '=', True), ('state', '=', "approved")]

class WebsiteSale(WebsiteSale):

    def validatePhone(self, phone):
        if phone[0] != '0':
            return False
        if len(phone) < 9:
            return False
        if len(phone) > 11:
            return False
        return True

    def checkout_form_validate(self, mode, all_form_values, data):
        # mode: tuple ('new|edit', 'billing|shipping')
        # all_form_values: all values before preprocess
        # data: values after preprocess
        error = dict()
        error_message = []

        # Required fields from form
        required_fields = [f for f in (all_form_values.get('field_required') or '').split(',') if f]
        # Required fields from mandatory field function
        required_fields += mode[1] == 'shipping' and self._get_mandatory_shipping_fields() or self._get_mandatory_billing_fields()
        # Check if state required
        country = request.env['res.country']
        if data.get('country_id'):
            country = country.browse(int(data.get('country_id')))
            if 'state_code' in country.get_address_fields() and country.state_ids:
                required_fields += ['state_id']

        # error message for empty required fields
        for field_name in required_fields:
            if not data.get(field_name):
                error[field_name] = 'missing'

        #name validation
        name = data.get('name')
        if True in [n.isdigit() for n in name]:
            error['name'] = 'invalid name'
            error_message.append(_('Invalid name. No digit allowed.'))
        if len(name) > 30:
            error['name'] = 'invalid name'
            error_message.append(_('Invalid name! Length is greater then 30.'))

        #street validation
        street = data.get('street')
        if len(street) > 80:
            error['street'] = 'street name too long'
            error_message.append(_('Address is too long. Please use two lines.'))

        # phone validation
        phone = data.get('phone')
        if phone and not self.validatePhone(phone):
            error['phone'] = 'error'
            error_message.append(_("Invalid Phone Number! Phone Number should start with '0' and length must be "
                                       "between 9 and 11"))
        # email validation
        if data.get('email') and not tools.single_email_re.match(data.get('email')):
            error["email"] = 'error'
            error_message.append(_('Invalid Email! Please enter a valid email address.'))

        # vat validation
        Partner = request.env['res.partner']
        if data.get("vat") and hasattr(Partner, "check_vat"):
            if data.get("country_id"):
                data["vat"] = Partner.fix_eu_vat_number(data.get("country_id"), data.get("vat"))
            partner_dummy = Partner.new({
                'vat': data['vat'],
                'country_id': (int(data['country_id'])
                               if data.get('country_id') else False),
            })
            try:
                partner_dummy.check_vat()
            except ValidationError:
                error["vat"] = 'error'

        if [err for err in error.values() if err == 'missing']:
            if len(error.keys()) == 1:
                for i in error.keys():
                    if i == 'township_id':
                        error.pop('township_id')
                        error.update({'Township': 'missing'})
                    elif i == 'country_id':
                        error.pop('country_id')
                        error.update({'Country': 'missing'})
                    elif i == 'street':
                        error.pop('street')
                        error.update({'Address': 'missing'})
                error_message.append(_('\n'.join("{}".format(k) for k in error.keys()) + ' is invalid'))
            else:
                error_message.append(_('Some required fields are empty or invalid.'))

        return error, error_message

    @http.route('/shop/payment/uploaded', type='http', auth="public", website=True, method=['POST'])
    def upload_files(self, **post):

        if post.get('attachment', False):
            name = post.get('attachment').filename
            if name and name.lower().endswith(('.png', '.jpeg', '.gif','jpg','tiff','raw')):
                file = post.get('attachment')
                sale_order_id = post.get('sale_order_id')
                attachment = file.read()
                image_64_encode = base64.encodestring(attachment)
                #image_64_decode = base64.decodestring(image_64_encode)
                sale_order_objs = request.env['sale.order'].sudo().search([("id", "=", int(sale_order_id))])

                if sale_order_objs:
                    for sale_order_obj in sale_order_objs:
                        sale_order_obj.sudo().write({'payment_upload_temp': image_64_encode, 'payment_upload_name': name})

        # sale_sorder_id = request.session.get('sale_last_order_id')
        # if sale_sorder_id:
        #     sorder = request.env['sale.order'].sudo().browse(sale_sorder_id)
        #     return request.render("do_customization.confirmation_payment_ss", {'order': sorder})
        # else:
        #     return request.redirect('/shop')

    @http.route('/faq', type='http', auth='public', website=True)
    def faq(self, search='', lang=None,  **post):

        faqs = request.env['website.faq'].search([('website_published', '=', True)])
        faq_categories = request.env['faq.category'].search([('website_published', '=', True)])

        domains = self._get_search_faq_domain(search)

        search_faq = faqs.search(domains)

        lang = get_lang(request.env)

        if "burmese" in lang.name.lower():
            myanmar = True
        else:
            myanmar = False

        values = {
            'myanmar': myanmar,
            'faq_categories': faq_categories,
            'faqs': search_faq,
            'domain': domains,
            'search': search
        }

        return request.render("do_customization.faq", values)

    @http.route('/create_seller_shop', type='http', auth='public', website=True)
    def create_seller_shop(self, search='', lang=None, **post):
        return request.render("do_customization.create_seller_shop")

    @http.route(['/shop/payment/transaction/',
                 '/shop/payment/transaction/<int:so_id>',
                 '/shop/payment/transaction/<int:so_id>/<string:access_token>'], type='json', auth="public", method=['POST'],
                website=True)
    def payment_transaction(self, acquirer_id, cod, preview=False, save_token=False, so_id=None, access_token=None, token=None, **post):
        """ Json method that creates a payment.transaction, used to create a
        transaction when the user clicks on 'pay now' button. After having
        created the transaction, the event continues and the user is redirected
        to the acquirer website.

        :param int acquirer_id: id of a payment.acquirer record. If not set the
                                user is redirected to the checkout page
        """
        sale_order = request.website.sale_get_order()
        if cod == 0 and sale_order.payment_upload_temp:
            sale_order.sudo().write({'payment_upload': sale_order.payment_upload_temp})
        else:
            sale_order.sudo().write({'payment_upload': None})

        if sale_order.selected_carrier_id:
            carrier = request.env['delivery.carrier'].sudo().search([('id', '=', sale_order.selected_carrier_id)])
            shipping_cost = carrier.rate_shipment(sale_order)['price'] if carrier.free_over else carrier.fixed_price
            sale_order.set_delivery_line(carrier, shipping_cost)

        # Ensure a payment acquirer is selected
        if not acquirer_id:
            return False

        try:
            acquirer_id = int(acquirer_id)

        except:
            return False

        # Retrieve the sale order
        if so_id:
            env = request.env['sale.order']
            domain = [('id', '=', so_id)]
            if access_token:
                env = env.sudo()
                domain.append(('access_token', '=', access_token))
            order = env.search(domain, limit=1)
        else:
            order = request.website.sale_get_order()


        # Ensure there is something to proceed
        if not order or (order and not order.order_line):
            return False

        assert order.partner_id.id != request.website.partner_id.id

        # Create transaction
        vals = {'acquirer_id': acquirer_id,
                'return_url': '/shop/payment/validate'}

        if save_token:
            vals['type'] = 'form_save'
        if token:
            vals['payment_token_id'] = int(token)

        transaction = order._create_payment_transaction(vals)

        # store the new transaction into the transaction list and if there's an old one, we remove it
        # until the day the ecommerce supports multiple orders at the same time
        last_tx_id = request.session.get('__website_sale_last_tx_id')
        last_tx = request.env['payment.transaction'].browse(last_tx_id).sudo().exists()
        if last_tx:
            PaymentProcessing.remove_payment_transaction(last_tx)
        PaymentProcessing.add_payment_transaction(transaction)
        request.session['__website_sale_last_tx_id'] = transaction.id
        return transaction.render_sale_button(order)

    @http.route('/shop/checkout/preview', type='http', method=['POST'], auth="public", website=True, csrf=False)
    def checkout_preview(self, **post):
        sale_order = request.website.sale_get_order()
        checked_length = request.website.get_checked_sale_order_line_length()
        if checked_length == 0:
            return request.redirect('/shop')

        acquirer_id = post.get('pm_id')
        if acquirer_id:
            sale_order.write({
                'selected_payment': int(acquirer_id)
            })
        acquirer = request.env["payment.acquirer"].search([('id', '=', sale_order.selected_payment)])
        if acquirer.display_as == 'Cash on Delivery':
            cod = "1"
        else:
            cod = "0"
        delivery = sale_order._check_delivery_selected()

        if sale_order.wk_coupon_value:
            checked_amount_untaxed = checked_amount_tax = 0.0
            for line in sale_order.order_line:
                if line.selected_checkout:
                    checked_amount_untaxed += line.price_subtotal
                    checked_amount_tax += line.price_tax

            sale_order.update({
                'checked_amount_untaxed': checked_amount_untaxed,
                'checked_amount_tax': checked_amount_tax,
                'checked_amount_total': checked_amount_untaxed + checked_amount_tax + sale_order.amount_delivery,
            })

        values = {
            'sale_order': sale_order,
            'acq': acquirer,
            'order': sale_order,
            'cod': cod,
            'delivery': delivery
        }
        return request.render("do_customization.checkout_preview", values)


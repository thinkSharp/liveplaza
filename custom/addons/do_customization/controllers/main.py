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

    @http.route('/shop/payment/uploaded', type='http', auth="public", website=True)
    def upload_files(self, **post):
        values = {}
        
        if post.get('attachment',False):
            name = post.get('attachment').filename
            if name and name.lower().endswith(('.png', '.jpeg', '.gif','jpg','tiff','raw')):   
                file = post.get('attachment')
                sale_order_id = post.get('sale_order_id')
                attachment = file.read() 
                image_64_encode = base64.encodestring(attachment)
                #image_64_decode = base64.decodestring(image_64_encode)
                order = request.env['sale.order'].sudo().browse(sale_order_id).exists()
                sale_order_objs = request.env['sale.order'].sudo().search([("id", "=", int(sale_order_id))])
                
                if sale_order_objs:
                    for sale_order_obj in sale_order_objs:
                        sale_order_obj.sudo().write({'payment_upload': image_64_encode, 'payment_upload_name': name})
                        
                values = {
                    'website_sale_order': order,
                    'order': order,
                }
            else:
                return request.redirect('/shop/confirmation')
        
        sale_sorder_id = request.session.get('sale_last_order_id')
        if sale_sorder_id:
            sorder = request.env['sale.order'].sudo().browse(sale_sorder_id)
            return request.render("do_customization.confirmation_payment_ss", {'order': sorder})
        else:
            return request.redirect('/shop')
        
        #return request.render("odoo_marketplace.confirmation_payment_ss", values)  #request.redirect('/shop/confirmation') #

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

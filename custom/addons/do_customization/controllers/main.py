import werkzeug
import odoo
from odoo.addons.auth_signup.models.res_users import SignupError
from odoo.addons.web.controllers.main import ensure_db
from odoo import http
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

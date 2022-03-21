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
import logging
_logger = logging.getLogger(__name__)
import urllib.parse as urlparse
import re
from urllib.parse import urlencode


PPG = 10000000  # Products Per Page
PPR = 4   # Products Per Row

SPG = 100000  # Shops/sellers Per Page
SPR = 4   # Shops/sellers Per Row


marketplace_domain = [('sale_ok', '=', True), ('state', '=', "approved")]

class WebsiteSale(WebsiteSale):

    @http.route('/shop/payment/uploaded', type='http', auth="public", website=True)
    def upload_files(self, **post):
        values = {}
        
        if post.get('attachment',False):
            name = post.get('attachment').filename      
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
        # else:
        #     return "Please select payment screenshot from your device and upload."  #"NotFound() #raise Warning(_("Please select payment screenshot from your device and upload."))
        
        sale_sorder_id = request.session.get('sale_last_order_id')
        if sale_sorder_id:
            sorder = request.env['sale.order'].sudo().browse(sale_sorder_id)
            return request.render("do_customization.confirmation_payment_ss", {'order': sorder})
        else:
            return request.redirect('/shop')
        
        #return request.render("odoo_marketplace.confirmation_payment_ss", values)  #request.redirect('/shop/confirmation') #
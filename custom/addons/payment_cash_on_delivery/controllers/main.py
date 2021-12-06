# -*- coding: utf-8 -*-
#################################################################################
#
#    Copyright (c) 2019-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>)
#    You should have received a copy of the License along with this program.
#    If not, see <https://store.webkul.com/license.html/>
#################################################################################
from odoo import http
from odoo.tools.translate import _
from odoo.http import request
import werkzeug


from odoo.addons.website_sale.controllers.main import WebsiteSale


class WebsiteSale(WebsiteSale):

    _codfeedbackUrl = '/payment/cash_on_delivery/feedback'
    @http.route([_codfeedbackUrl], type='http', auth='public', website=True)
    def cod_payment(self, **post):
        request.env['payment.transaction'].form_feedback(
            post, 'cash_on_delivery')
        return werkzeug.utils.redirect('/shop/payment/validate')

    @http.route()
    def product(self, product, category='', search='', **kwargs):
        res = super(WebsiteSale, self).product(
            product, category=category, search=search, **kwargs)

        cod_rule = request.env['payment.acquirer'].sudo().search([('provider', '=', 'cash_on_delivery')], limit=1).cod_rule
        is_cod_available = request.website.is_cod_available(product)
        res.qcontext['cod_availability'] = is_cod_available
        res.qcontext['cod_rule'] = cod_rule
        return res

    @http.route()
    def payment(self, **post):
        res = super(WebsiteSale, self).payment(**post)
        acquirers = res.qcontext.get('acquirers', [])
        errors = res.qcontext.get('errors', [])
        for acquirer in filter(lambda ac: ac.provider == 'cash_on_delivery', acquirers):
            if not request.website.is_cod_available(payment_acquirer=acquirer):
                if acquirer.cod_rule.cod_payment_btn == 'hide':
                    acquirers.remove(acquirer)
                    errors.append(
                        ((_('Sorry, We are unable to provide Cash On Delivery.')), acquirer.cod_rule.cod_unavailability_payment_message))
                else:
                    res.qcontext['cod_errors']= [_('Sorry, We are unable to provide Cash On Delivery.'), acquirer.cod_rule.cod_unavailability_payment_message]
                    res.qcontext['isCodDisable'] = True
        res.qcontext['acquirers'] = acquirers
        res.qcontext['errors'] = errors 
        return res

    @http.route()
    def payment_transaction(self, acquirer_id, save_token=False, so_id=None, access_token=None, token=None, **kwargs):
        cod_payment = request.env['payment.acquirer'].sudo().search(
            [('provider', '=', 'cash_on_delivery')], limit=1
        )
        if acquirer_id == cod_payment.id and not request.website.is_cod_available(payment_acquirer=cod_payment):
            return False
        return super(WebsiteSale, self).payment_transaction(acquirer_id=acquirer_id, save_token=save_token, so_id=so_id, access_token=access_token, token=token, **kwargs)

# -*- coding: utf-8 -*-
##############################################################################
# Copyright (c) 2016-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>)
# See LICENSE file for full copyright and licensing details.
# License URL : <https://store.webkul.com/license.html/>
##############################################################################
import logging
import pprint
import requests
import json
import base64
import hmac,hashlib


import werkzeug
from werkzeug.utils import redirect

from odoo import http
from odoo.http import request
from odoo.exceptions import ValidationError


_logger = logging.getLogger(__name__)


_return_url = '/payment/wavepay/return/'
_cancel_url = '/payment/wavepay/cancel/'



def hash_hmac(data,key):

    timeToLiveSeconds     = data["time_to_live_in_seconds"]
    merchant_id           = data["merchant_id"]
    order_id              = data["order_id"]
    amount                = data["amount"]
    backend_result_url    = data["backend_result_url"]
    merchant_reference_id = data["merchant_reference_id"]
    data = [timeToLiveSeconds,
            merchant_id,
            order_id,
            amount,
            backend_result_url,
            merchant_reference_id]
    data = ''.join(data)
    data = bytes(data, 'utf-8')

    secret = bytes(key, 'utf-8')

    dig = hmac.new(secret, msg=data, digestmod=hashlib.sha256)

    return dig.hexdigest()

def _payment_capture(data,url):

    url = url+"/payment"

    headers = {
        'Accept': "application/json",
    }

    files = []

    try:
        r = requests.request("POST", url, headers=headers, data=data, files=files,verify=False)
        r = r.json()
        return r
    except Exception as e:
        return {}




class WavePayController(http.Controller):


    @http.route('/payment/wavepay/token/create', type='json', auth='public', csrf=False)
    def create_wavepay_checkout(self, **post):

        tx = request.env['payment.transaction'].sudo().search([('id','=',int(post.get('txId', 0)))])

        if tx:
            base_url = request.env['ir.config_parameter'].sudo().get_param('web.base.url')
            acq = tx.acquirer_id
            partner_id = tx.partner_id
            request.session['network_order'] = tx.reference


            if acq.state == 'enabled':
                payment_url = "https://payments.wavemoney.io"
            elif acq.state == 'test':
                payment_url = "https://testpayments.wavemoney.io:8107"



            timeToLiveSeconds     = '5000'
            merchant_id           = acq.wavepay_merchant_id
            secret_key           = acq.wavepay_secret_key

            order_id              = str(tx.sale_order_ids.id)
            amount                = str(int(tx.amount))
            backend_result_url    = base_url+_return_url
            merchant_reference_id = tx.sale_order_ids.name
            payment_reference_id = tx.reference #New field added

            items = [
                {
                    'name':line.product_id.name,
                    'amount':int(line.price_subtotal)
                }for line in tx.sale_order_ids.website_order_line if line.selected_checkout
            ]

            for line in tx.sale_order_ids.order_line:
                if line.is_delivery:
                    items.append({'name': line.product_id.name, 'amount': line.price_subtotal})

            hashing_dict = {
                "time_to_live_in_seconds": timeToLiveSeconds,
                "merchant_id"            : merchant_id,
                "order_id"               : order_id,
                "amount"                 : amount,
                "backend_result_url"     : backend_result_url,
                "merchant_reference_id"  : merchant_reference_id,
            }


            data={
                'time_to_live_in_seconds': timeToLiveSeconds,
                'merchant_id'            : merchant_id,
                'order_id'               : order_id,
                'merchant_reference_id'  : merchant_reference_id,
                'payment_reference_id'   : payment_reference_id,
                'frontend_result_url'    : base_url,
                'backend_result_url'     : backend_result_url,
                'amount'                 : amount,
                'payment_description'    : 'Payment for Order No.' + merchant_reference_id,
                'merchant_name'          : partner_id.name,
                'items'                  : json.dumps(items),
                'hash'                   : hash_hmac(hashing_dict,acq.wavepay_secret_key)
            }

            res = _payment_capture(data,payment_url)

            if res:
                if res.get('message') == 'success':
                    r = res.update({'url':payment_url+"/authenticate?transaction_id="+res['transaction_id']})
                return json.dumps(res)

        return None

    @http.route([_return_url, _cancel_url], type='http', auth="public", methods=['POST', 'GET'], csrf=False)
    def wavepay_dpn(self, **post):
        """ WavePay DPN """
        _logger.info('Beginning WavePay DPN form_feedback with post data %s', pprint.pformat(post))  # debug
        try:
            request.env['payment.transaction'].sudo().form_feedback(post, 'wavepay')
        except ValidationError:
            _logger.exception('Unable to validate the WavePay payment')
        return werkzeug.utils.redirect('/payment/process')

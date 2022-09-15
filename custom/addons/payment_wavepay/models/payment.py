# -*- coding: utf-8 -*-
##############################################################################
# Copyright (c) 2016-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>)
# See LICENSE file for full copyright and licensing details.
# License URL : <https://store.webkul.com/license.html/>
##############################################################################
import logging
import json
from werkzeug import urls

from odoo import api, fields, models, _
# from odoo.addons.payment_wavepay.controllers.main import WavePayController
from odoo.addons.payment.models.payment_acquirer import ValidationError

_logger = logging.getLogger(__name__)


class PaymentAcquirerWavePay(models.Model):
    _inherit = 'payment.acquirer'

    provider = fields.Selection(selection_add=[('wavepay', 'WavePay')])
    wavepay_merchant_id = fields.Char('Merchant Id', required_if_provider='wavepay',groups='base.group_user')
    wavepay_secret_key = fields.Char('Secret Key', required_if_provider='wavepay',groups='base.group_user')


    def wavepay_form_generate_values(self ,values):
        wavepay_tx_values = dict(values)
        if values.get('reference','/') != "/":
            tx = self.env['payment.transaction'].sudo().search([('reference', '=', values.get('reference'))])
            wavepay_tx_values.update({
                "txId": tx.id,
                "secretId": self.wavepay_merchant_id,
                "merchantId": self.wavepay_secret_key,
            })
        return wavepay_tx_values

class PaymentTransactionWavePay(models.Model):
    _inherit = 'payment.transaction'

    @api.model
    def _wavepay_form_get_tx_from_data(self, data):
        reference = data.get('merchantReferenceId')
        if data.get('Status'):
            if not data["Status"]=="PAYMENT_CONFIRMED":
                error_msg = _('WavePay: received data with missing reference (%s)') % (reference)
                _logger.info(error_msg)
                raise ValidationError(error_msg)

        txs=self.env ['payment.transaction'].search([('reference' ,'=' ,reference)])
        if not txs or len (txs) > 1:
            error_msg='WavePay: received data for reference %s' % (reference)
            if not txs:
                error_msg+='; no order found'
            else:
                error_msg+='; multiple order found'
            _logger.info (error_msg)
            raise ValidationError (error_msg)
        return txs[0]

    def _wavepay_form_validate(self ,data):
        status=data["Status"]
        res = {
            'acquirer_reference': self.acquirer_id.name,
            'date': fields.Datetime.now(),
        }
        result=self.write(res)
        if status == 'PAYMENT_CONFIRMED':
            self._set_transaction_done()
        elif status == 'INSUFFICIENT_BALANCE':
            self._set_transaction_pending()
        else:
            self._set_transaction_cancel()
        return result

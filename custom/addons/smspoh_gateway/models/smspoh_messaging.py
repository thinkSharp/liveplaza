# -*- coding: utf-8 -*-
##############################################################################
#
# Odoo, Open Source Management Solution
# Copyright (C) 2016 Webkul Software Pvt. Ltd.
# Author : www.webkul.com
#
##############################################################################
import logging
import requests
import json
from urllib3.exceptions import HTTPError
from odoo import models, fields, api, _
from odoo.exceptions import except_orm, Warning, RedirectWarning

_logger = logging.getLogger(__name__)

def send_sms_using_smspoh(body_sms, mob_no, from_mob=None, sms_gateway=None, test=False):
    '''
    This function is designed for sending sms using smspoh SMS API.

    :param body_sms: body of sms contains text
    :param mob_no: Here mob_no must be string having one or more number
     seprated by (,)
    :param from_mob: sender mobile number or id used in smspoh API
    :param sms_gateway: sms.mail.server config object for smspoh Credentials
    :return: response dictionary if sms successfully sent else empty dictionary
    '''
    if not sms_gateway or not body_sms or not mob_no:
        return {}
    if sms_gateway.gateway == "smspoh":
        try:
            if sms_gateway.smspoh_api_key:
                headers = {
                'Authorization': 'Bearer %s'%(sms_gateway.smspoh_api_key),
                'Content-Type': 'application/json',
            }
            for mobi_no in mob_no.split(','):
                data = {'to':mobi_no, "message":body_sms, "sender":sms_gateway.smspoh_sender}
                if test:
                    data.update({"test":1})
                res = requests.post('https://smspoh.com/api/v2/send', headers=headers, data=json.dumps(data))
                return res.json()
        except HTTPError as e:
            logging.info(
                '---------------Smspoh HTTPError--------------\
                --------', exc_info=True)
            _logger.info(
                "---------------smspoh HTTPError While Sending SMS ----%r---\
                ------", e)
            return {}
        except Exception as e:
            logging.info(
                '---------------smspoh Exception While Sending SMS -----\
                -----', exc_info=True)
            _logger.info(
                "---------------smspoh Exception While Sending SMS -----%r----\
                -----", e)
            return {}
    return {}


class SmsSms(models.Model):
    """SMS sending using smspoh SMS Gateway."""

    _inherit = "wk.sms.sms"
    _name = "wk.sms.sms"
    _description = "smspoh SMS"


    def send_sms_via_gateway(
            self, body_sms, mob_no, from_mob=None, sms_gateway=None):
        self.ensure_one()
        gateway_id = sms_gateway if sms_gateway else super(
            SmsSms, self).send_sms_via_gateway(
            body_sms, mob_no, from_mob=from_mob, sms_gateway=sms_gateway)
        if gateway_id:
            if gateway_id.gateway == 'smspoh':
                for element in mob_no:
                    for mobi_no in element.split(','):
                        response = send_sms_using_smspoh(
                            body_sms, mobi_no, from_mob=from_mob,
                            sms_gateway=gateway_id)
                        sms_report_obj = self.env["sms.report"].create(
                            {
                                'to': mobi_no, 'msg': body_sms,
                                'sms_sms_id': self.id,
                                "auto_delete": self.auto_delete,
                                'sms_gateway_config_id': gateway_id.id})
                        vals = {'state':'undelivered'}
                        if response.get('status'):
                            message_data = response.get('data').get("messages")[0]
                            vals['smspoh_sms_id'] = message_data.get('id')
                            vals['state'] = 'sent'
                            vals['message'] = False
                        else:
                            message_data = response.get('error').get("messages")
                            vals.update({'state': 'failed','message':message_data})
                        if sms_report_obj:
                            sms_report_obj.write(vals)
                    else:
                        self.write({'state': 'error'})
                else:
                    self.write({'state': 'sent'})
            else:
                gateway_id = super(SmsSms, self).send_sms_via_gateway(
                    body_sms, mob_no, from_mob=from_mob,
                    sms_gateway=sms_gateway)
        else:
            _logger.info(
                "----------------------------- SMS Gateway not found ----------\
                ---------------")
        return gateway_id


class SmsReport(models.Model):
    """SMS report."""

    _inherit = "sms.report"

    smspoh_sms_id = fields.Char("smspoh SMS ID")

    @api.model
    def cron_function_for_sms(self):
        _logger.info(
            "************** Cron Function For smspoh SMS *******************")
        all_sms_report = self.search([('state', 'in', ('sent', 'new')),('sms_gateway','=','smspoh')])
        for sms in all_sms_report:
            sms_sms_obj = sms.sms_sms_id if sms.sms_sms_id else False
            if not sms.smspoh_sms_id:
                sms.send_now()
        super(SmsReport, self).cron_function_for_sms()
        return True

    def send_sms_via_gateway(
            self, body_sms, mob_no, from_mob=None, sms_gateway=None):
        self.ensure_one()
        gateway_id = sms_gateway if sms_gateway else super(
            SmsReport, self).send_sms_via_gateway(
            body_sms, mob_no, from_mob=from_mob, sms_gateway=sms_gateway)
        if gateway_id:
            if gateway_id.gateway == 'smspoh':
                if mob_no:
                    for element in mob_no:
                        count = 1
                        for mobi_no in element.split(','):
                            if count == 1:
                                self.to = mobi_no
                                rec = self
                            else:
                                rec = self.create({
                                    'to': mobi_no, 'msg': body_sms,
                                    "auto_delete": self.auto_delete,
                                    'sms_gateway_config_id': gateway_id.id})
                            response = send_sms_using_smspoh(
                                body_sms, mobi_no, from_mob=from_mob,
                                sms_gateway=gateway_id)
                            vals = {'state':'undelivered'}
                            if response.get('status'):
                                message_data = response.get('data').get("messages")[0]
                                vals['smspoh_sms_id'] = message_data.get('id')
                                vals['state'] = 'sent'
                                vals['message'] = False
                            else:
                                message_data = response.get('error').get("messages")[0]
                                vals.update({'state': 'failed','message':message_data})
                            rec.write(vals)
                            count += 1
                else:
                    self.write({'state': 'sent'})
            else:
                gateway_id = super(SmsReport, self).send_sms_via_gateway(
                    body_sms, mob_no, from_mob=from_mob,
                    sms_gateway=sms_gateway)
        return gateway_id

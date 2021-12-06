# -*- coding: utf-8 -*-
#################################################################################
#
# Copyright (c) 2019-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>:wink:
# See LICENSE file for full copyright and licensing details.
#################################################################################

from odoo import models, fields, api, _
from odoo.addons.payment.models.payment_acquirer import ValidationError
from odoo.addons.payment_cash_on_delivery.controllers.main import WebsiteSale
from odoo.http import request
from datetime import date,datetime
from dateutil import relativedelta
import logging
_logger = logging.getLogger(__name__)

HelpState = _(
    """Allowed  State(s) from COD Availability,For
        Allowing all State just set it to be blank"""
    )
HelpZip =_(
    """Enter comma separated Zip codes like:-
        WC2N,201301,21044,400001,460001,970001,
        For Allowing all zip just set it to be blank!"""
    )

HelpPolicy = _(
    """Enter Policy and Authenticity
        content to be display  on Product Page"""
    )
class WkCODApplicabilityRule(models.Model):
    _name = 'wk.cod.applicability.rule'
    _description=" Cod Applicability Rules"
    allowed_country_list = fields.Many2one(
        "res.country", required=1, string='Allow Country')
    allowed_state_list = fields.Many2many(
            "res.country.state",
            "wk_payment_acquirer_cod_rule_wk_res_country_state_relation",
            "wk_payment_acquirer_cod_rule",
            "wk_cod_res_country_sate",
            "Allow  State(s)",
            help=HelpState
        )
    zipcode_list = fields.Text(
            string='ZipCodes',
            help=HelpZip
        )
    cod_fk = fields.Many2one("wk.cod")


class WkCOD(models.Model):
    _name = 'wk.cod'
    _description = "Webkul Cash On Delivery"
    name = fields.Char(string='Name', default='Default Rule')
    
    def _default_policy_content(self):
        user = self.env.user
        currency_id = user.company_id.currency_id
        currency_symbol, symbol_position = currency_id.symbol, currency_id.position
        min_order_amount, max_order_amount = self.min_order_amount or 100, self.max_order_amount or 1000000
        if currency_symbol:
            min_order_amount = str(min_order_amount)+" "+str(currency_symbol) if symbol_position =="after" else str(currency_symbol)+" "+str(min_order_amount)
            max_order_amount = str(max_order_amount)+" "+str(currency_symbol) if symbol_position =="after" else str(currency_symbol)+" "+str(max_order_amount)
            policy_content = "Order Amount Must Be in Between {} to {}".format(min_order_amount, max_order_amount)
            return policy_content
        else:
            return "Order Order Amount Must Be in Between 100€ 100000€"
             

    min_order_amount = fields.Float(
            string='Min Order Amount',
            required=1,
            default=100,
            help='Minimum Order Amount for COD Availability'
        )
    max_order_amount = fields.Float(
            string='Max Order Amount',
            required=1,
            default=10000,
            help='Maximum Order Amount for COD Availability'
        )
    currency_id = fields.Many2one('res.currency', string='Currency', default=lambda self: self.env.user.company_id.currency_id)
    exclude_product = fields.Many2many(
            "product.template",
            "wk_payment_acquirer_cod_wk_product_template_relation",
            "wk_payment_acquirer_cod",
            "wk_product_template",
            "Exclude Product(s)",
            help='Exclude Product(s) from COD Availability'
        )
    cod_applicability = fields.One2many(
            comodel_name='wk.cod.applicability.rule',
            inverse_name='cod_fk',
            string='COD Applicability',
            required=1
        )
    # show_expected_cod_date = fields.Boolean(
    #         string='Show Delivered By Date',
    #         default=True,
    #         help='Show Expected COD Date Of Delivery on Product Page'
    #     )
    show_policy = fields.Boolean(
            string='Show Policy',
            default=True,
            help='Show Policy and Authenticity  on Product Page'
        )
    policy_content = fields.Char(
            string='Policy Content',
            default=_default_policy_content,
            help=HelpPolicy)
    cod_availability_message = fields.Char(
        string='Availability Message',
        default='COD AVAILABLE !',
        help='Enter Availability Message  content to be display  on Product Page'
    )
    cod_unavailability_message = fields.Char(
        string='Unavailability Message',
        default='Currently we do not provide COD for this item !',
        help='Enter Availability Message  content to be display  on Product Page'
     )
    cod_unavailability_payment_message = fields.Text(
        string='Unavailability Message on Payment',
        default='Some  product in your cart can not delivered  through Cash On Delivery ',
        help='Enter Unavailability Message  content to be display  on Payment Page'
    )
    cod_payment_btn = fields.Selection([
                                ('hide', 'Hide'),
                                ('disable', 'Disable')
                            ], "COD Payment Button",
                            default='disable',
                            help="Display light text on a dark background")

    @api.onchange('min_order_amount', 'max_order_amount', 'currency_id')
    def onchangeMinMaxAmount(self):
        for codObj in self:
            min_order_amount, max_order_amount = codObj.min_order_amount or 100, codObj.max_order_amount or 1000000
            currency_symbol = codObj.currency_id and codObj.currency_id.symbol
            symbol_position = codObj.currency_id and codObj.currency_id.position
            if currency_symbol:
                min_order_amount = str(min_order_amount)+" "+str(currency_symbol) if symbol_position =="after" else str(currency_symbol)+" "+str(min_order_amount)
                max_order_amount = str(max_order_amount)+" "+str(currency_symbol) if symbol_position =="after" else str(currency_symbol)+" "+str(max_order_amount)
            codObj.policy_content = "Order Amount Must Be in Between {} to {}".format(min_order_amount, max_order_amount)

    @api.model
    @api.constrains('min_order_amount', 'min_order_amount')
    def _check_order_limit(self):
        """	A private method to validate the Order limit!"""
        if self.min_order_amount <= 0 or self.max_order_amount <= 0:
            raise ValidationError(_("Order Limit Can't be Negative"))
        elif self.min_order_amount >= self.max_order_amount:
            raise ValidationError(_("Minimum Order Amount will be smaller  than  Maximum   Order Amount"))

    @api.model
    def check_zipcode_list(self, partner_id,  zipcode_list):
        return partner_id.zip if partner_id and partner_id.zip and zipcode_list and (partner_id.zip.strip().upper() in zipcode_list.strip().upper().split(',')) else False

    @api.model
    def check_state_list(self, partner_id,  allowed_state_list):
        code = partner_id and partner_id.state_id.code
        return allowed_state_list.filtered(lambda st: code in st.mapped('code'))

    @api.model
    def check_country_list(self, partner_id):
        code = partner_id and partner_id.country_id.code
        # rule = self.cod_applicability.mapped('allowed_country_list.code')
        cod_applicability = self.cod_applicability.filtered(lambda ap: code in ap.mapped('allowed_country_list.code'))
        if cod_applicability:
            return cod_applicability
        return []



class website(models.Model):
    _inherit = 'website'

    @api.model
    def is_cod_available(self, product=None, payment_acquirer=None):
        cod = request.env['payment.acquirer'].sudo().search([('provider', '=', 'cash_on_delivery')], limit=1)
        order = request.website.sale_get_order()
        recipient = order and order.partner_shipping_id and order.partner_shipping_id or request.env.user.partner_id
        if product and cod.cod_rule:
            return cod.validate_address(recipient) and product.id not in[product_item.id for product_item in cod.cod_rule.exclude_product]
        if payment_acquirer and payment_acquirer.provider == 'cash_on_delivery' and cod.cod_rule:
            product_in_line = set(
                order_line.product_id.product_tmpl_id.id for order_line in order.order_line)
            exclude_product = set(
                product_item.id for product_item in cod.cod_rule.exclude_product)
            return cod.validate_address(recipient) and order.amount_total >= cod.cod_rule.min_order_amount and order.amount_total <= cod.cod_rule.max_order_amount and not product_in_line & exclude_product
        return True

    # @api.model
    # def expected_cod_date(self, product):
    #     res = (date.today() + relativedelta.relativedelta(days=+int(product.sale_delay))).strftime("%d.%m.%Y")
    #     return res

class AcquirerCOD(models.Model):
    _inherit = 'payment.acquirer'

    cod_rule = fields.Many2one("wk.cod", "COD Availability Rule")
    provider = fields.Selection(selection_add=[('cash_on_delivery', 'COD')])

    @api.model
    def _create_missing_journal_for_acquirers(self, company=None):
        # By default, the wire transfer method uses the default Bank journal.
        company = company or self.env.user.company_id
        acquirers = self.env['payment.acquirer'].search(
            [('provider', '=', 'cash_on_delivery'), ('journal_id', '=', False), ('company_id', '=', company.id)])

        bank_journal = self.env['account.journal'].search(
            [('type', '=', 'bank'), ('company_id', '=', company.id)], limit=1)
        if bank_journal:
            acquirers.write({'journal_id': bank_journal.id})
        return super(AcquirerCOD, self)._create_missing_journal_for_acquirers(company=company)

    @api.model
    def validate_address(self, partner_id):
        checkstate = True
        checkzip = True
        cod_applicabilitys = self.cod_rule.check_country_list(partner_id)
        for cod_applicability in cod_applicabilitys:
            if cod_applicability:
                if cod_applicability.allowed_state_list:
                    checkstate = self.cod_rule.check_state_list(partner_id, cod_applicability.allowed_state_list)
                if cod_applicability.zipcode_list:
                    checkzip = self.cod_rule.check_zipcode_list(partner_id, cod_applicability.zipcode_list)
                return checkstate and checkzip
        else:
            return False

    @api.model
    def cash_on_delivery_get_form_action_url(self):
        self.ensure_one()
        return WebsiteSale._codfeedbackUrl


class TxCOD(models.Model):
    _inherit = 'payment.transaction'
    provider = fields.Selection(
        string='Providers', selection=[('cash_on_delivery','COD')])


    @api.model
    def _cash_on_delivery_form_get_tx_from_data(self, data):
        reference = data.get('reference')
        if not reference:
            error_msg = _('COD: received data with missing reference (%s) or payment has not been captured ' % (
                reference))
            _logger.warning("# %r----%r"%(error_msg, data))
            raise ValidationError(error_msg)
        tx = self.sudo().search([('reference', '=', reference)])
        if not tx or len(tx) > 1:
            message = tx and 'Multiple order found'or 'No order found'
            error_msg = _('COD: Received data for reference %s .%s.' % (
                reference, message))
            _logger.warning(error_msg)
            raise ValidationError(error_msg)
        return tx

    @api.model
    def _cash_on_delivery_form_get_invalid_parameters(self,data):
        invalid_parameters = []
        return invalid_parameters

    @api.model
    def _cash_on_delivery_form_validate(self,  data):
        _logger.info('Validated transfer payment for tx %s: set as pending' % (self.reference))
        self._set_transaction_pending()
        return True

    @api.model
    def _cron_post_process_after_done(self):
        if not self:
            ten_minutes_ago = datetime.now() - relativedelta.relativedelta(minutes=10)
            # we retrieve all the payment tx that need to be post processed
            self = self.search([('state', '=', 'done'),
                                ('is_processed', '=', False),
                                ('date', '<=', ten_minutes_ago),
                            ])
        for tx in self:
            if tx.provider == "cash_on_delivery":
                continue
            try:
                tx._post_process_after_done()
                self.env.cr.commit()
            except Exception as e:
                _logger.exception("Transaction post processing failed")
                self.env.cr.rollback()

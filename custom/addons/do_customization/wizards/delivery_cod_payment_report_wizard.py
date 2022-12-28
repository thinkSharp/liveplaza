# -*- coding: utf-8 -*-

from odoo import api, fields, models, tools, _
from datetime import datetime

from odoo.exceptions import ValidationError, UserError, Warning


class DeliveryCODPaymentReportWizard(models.TransientModel):
    _name = 'delivery.cod.payment.wizard'

    start_date = fields.Date('Start Date', default=datetime.today())
    end_date = fields.Date('End Date', default=datetime.today())
    delivery_person_id = fields.Many2one('res.partner', string='Delivery Person', required=True,
                                domain=['|',('delivery_vendor', '=', True),('picking_vendor', '=', True)], copy=False)

    def generate_order_report(self):
        vals = []
        report_data = {}

        records = self.env['delivery.cod.payment.result'].search([])

        if records:
            records.unlink()

        if self.delivery_person_id:
            report_data = self._calculate_delivery_dvr(self.delivery_person_id, self.start_date, self.end_date)

        for v_data in report_data:
            res = {
                'start_date': self.start_date,
                'end_date': self.end_date,
                'report_date': datetime.today(),
                'payment_type': v_data.get("payment_type"),
                'delivery_status': v_data.get("delivery_status"),
                'order_number': v_data.get("order_number"),
                'paid_amount': v_data.get("paid_amount"),
                'delivery_person': v_data.get("delivery_person"),
                'do_date': v_data.get("do_date"),
            }

            vals.append(res)

        if vals:
            self.env['delivery.cod.payment.result'].create(vals)
            wizard_form = self.env.ref('delivery_cod_payment_result_tree', False)

            return {
                'name': 'Delivery COD Payment Report',
                'type': 'ir.actions.act_window',
                'view_type': 'form',
                'view_mode': 'tree',
                'res_model': 'delivery.cod.payment.result',
                'views': [(wizard_form, 'tree')],
                # 'domain' : [('mp_seller_name','=', self.env.user.partner_id.name)],
                'target': 'current',
            }
        else:
            raise ValidationError(_("No records found."))

    def _calculate_delivery_dvr(self, delivery_person_id, start_date, end_date):
        for obj in delivery_person_id:
            query = '''
                SELECT rp.name delivery_person, sp.paid_amount,sp.origin order_number,sp.scheduled_date do_date,
                CASE WHEN sp.payment_provider='cash_on_delivery' THEN 'COD' END payment_type,
                CASE WHEN sp.state='done' THEN 'DONE'
                WHEN sp.state ='delivering' THEN 'Delivering Now'
                WHEN sp.state ='confirmed' THEN 'Waiting'
                WHEN sp.state ='assigned' THEN 'Ready'
                WHEN sp.state ='waiting' THEN 'Waiting Another Operation'
                WHEN sp.state ='cancel' THEN 'Cancelled'
                WHEN sp.state ='hold' THEN 'Hold'
                WHEN sp.state ='draft' THEN 'Draft' END delivery_status
                FROM stock_picking sp
                INNER JOIN res_partner rp ON rp.id=sp.delivery_person_id
                WHERE 1=1
                AND sp.payment_provider='cash_on_delivery' 
                AND sp.scheduled_date BETWEEN %s AND %s
                AND sp.delivery_person_id = %s
                GROUP BY rp.name,sp.paid_amount,sp.origin,sp.payment_provider,sp.origin,do_date,sp.state'''
            self.env.cr.execute(query, (start_date,end_date,delivery_person_id.id,))
            query_res = self._cr.dictfetchall()
            return query_res

class DeliveryCODPaymentResult(models.TransientModel):
    _name = 'delivery.cod.payment.result'

    start_date = fields.Date('From Date')
    end_date = fields.Date('To Date')
    report_date = fields.Date('Report Date', default=datetime.today())

    delivery_person = fields.Char('Delivery Person')
    payment_type = fields.Char('Payment Type')
    delivery_status = fields.Char('Status')

    order_number = fields.Char('Order Number')
    paid_amount = fields.Char('Paid Amount')
    do_date = fields.Date('Delivery Date')



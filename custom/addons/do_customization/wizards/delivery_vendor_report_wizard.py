# -*- coding: utf-8 -*-

from odoo import api, fields, models, tools, _
from datetime import datetime
import json
from odoo.exceptions import ValidationError, UserError, Warning


class DVRDeliveryReportWizard(models.TransientModel):
    _name = 'dvr.delivery.wizard'

    start_date = fields.Date('Start Date', default=datetime.today())
    end_date = fields.Date('End Date', default=datetime.today())
    vendor_id = fields.Many2one('res.partner', string='Delivery Vendor', required=True, copy=False)
    vendor_domain = fields.Char(compute="_compute_vendor_domain", readonly=True, store=False)

    @api.depends('vendor_id')
    def _compute_vendor_domain(self):
        for rec in self:
            vendor_list = []
            user_obj = self.env['res.users'].sudo().browse(self._uid)
            if user_obj.partner_id:
                if user_obj.has_group('access_rights_customization.group_delivery_operator') or user_obj.has_group('access_rights_customization.group_pickupandpackaging_operator'):
                    vendor_list.append(user_obj.partner_id.id)  #self.env['res.partner'].search([('is_default', '=', True), ('active', '=', True)])
                elif user_obj.has_group('picking_and_delivery_vendor.pickup_vendor_group') or user_obj.has_group('picking_and_delivery_vendor.delivery_vendor_group'):
                    vendor_list.append(user_obj.partner_id.id)
                else:  #user_obj.has_group('base.group_system') or user_obj.has_group('picking_and_delivery_vendor.pickup_vendor_group') or user_obj.has_group('picking_and_delivery_vendor.delivery_vendor_group'):
                    vendor_ids = self.env['res.partner'].search([('is_default', '=', True), ('active', '=', True)])
                    if vendor_ids:
                        for vids in vendor_ids:
                            vendor_list.append(vids.id)

            rec.vendor_domain = json.dumps([('id', 'in', vendor_list)])

    def generate_order_report(self):
        vals = []
        vendor_data = {}

        records = self.env['dvr.delivery.result'].search([])

        if records:
            records.unlink()

        if self.vendor_id:
            vendor_data = self._calculate_delivery_dvr(self.vendor_id, self.start_date, self.end_date)

        for v_data in vendor_data:
            res = {
                'start_date': self.start_date,
                'end_date': self.end_date,
                'report_date': datetime.today(),
                'dvr_vendor_name': self.vendor_id.name,
                'dvr_picking_type': v_data.get("dvr_picking_type"),
                'dvr_status': v_data.get("dvr_status"),
                'dvr_order_number': v_data.get("dvr_order_number"),
                'dvr_reference': v_data.get("dvr_reference"),
                'dvr_pickup_person_name': v_data.get("dvr_pickup_person_name"),
                'dvr_delivery_person_name': v_data.get("dvr_delivery_person_name"),
                'picking_date': v_data.get("picking_date"),
            }

            vals.append(res)

        if vals:
            self.env['dvr.delivery.result'].create(vals)
            wizard_form = self.env.ref('dvr_delivery_result_tree', False)

            return {
                'name': 'Delivery Vendor Report',
                'type': 'ir.actions.act_window',
                'view_type': 'form',
                'view_mode': 'tree',
                'res_model': 'dvr.delivery.result',
                'views': [(wizard_form, 'tree')],
                # 'domain' : [('mp_seller_name','=', self.env.user.partner_id.name)],
                'target': 'current',
            }
        else:
            raise ValidationError(_("No records found."))

    def _calculate_delivery_dvr(self, vendor_id, start_date, end_date):
        for obj in vendor_id:
            query = '''
                SELECT sp.scheduled_date,sp.name dvr_reference,sp.origin dvr_order_number,rp.name dvr_vendor_name,
                spt.name dvr_picking_type,
                CASE WHEN sp.state='done' THEN 'DONE'
                WHEN sp.state ='delivering' THEN 'Delivering Now'
                WHEN sp.state ='confirmed' THEN 'Waiting'
                WHEN sp.state ='assigned' THEN 'Ready'
                WHEN sp.state ='waiting' THEN 'Waiting Another Operation'
                WHEN sp.state ='cancel' THEN 'Cancelled'
                WHEN sp.state ='hold' THEN 'Hold'
                WHEN sp.state ='draft' THEN 'Draft' END dvr_status,
                sp.pick_date picking_date, pp.name dvr_pickup_person,dp.name dvr_delivery_person
                FROM stock_picking sp 
                INNER JOIN stock_picking_type spt ON spt.id=sp.picking_type_id
                INNER JOIN res_partner rp ON rp.id=sp.vendor_id
                LEFT JOIN res_partner pp ON pp.id=sp.pickup_person_id
                LEFT JOIN res_partner dp ON dp.id=sp.delivery_person_id
                WHERE 1=1
                AND sp.scheduled_date::DATE BETWEEN %s AND %s
                AND sp.vendor_id = %s
                ORDER BY sp.id'''
            self.env.cr.execute(query, (start_date,end_date,vendor_id.id,))
            query_res = self._cr.dictfetchall()
            return query_res

class DVRDeliveryResult(models.TransientModel):
    _name = 'dvr.delivery.result'

    start_date = fields.Date('From Date')
    end_date = fields.Date('To Date')
    report_date = fields.Date('Report Date', default=datetime.today())

    dvr_vendor_name = fields.Char('Vendor')
    dvr_picking_type = fields.Char('Type')
    dvr_status = fields.Char('Status')

    dvr_order_number = fields.Char('Order Number')
    dvr_reference = fields.Char('Reference')
    dvr_pickup_person_name = fields.Char('Pickup Person')
    dvr_delivery_person_name = fields.Char('Delivery Person')
    picking_date = fields.Date('Pick Date')



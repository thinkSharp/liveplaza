# -*- coding: utf-8 -*-

from odoo import api, fields, models, tools, _
from datetime import datetime
import json
from odoo.exceptions import ValidationError, UserError, Warning


class DPRDeliveryReportWizard(models.TransientModel):
    _name = 'dpr.delivery.wizard'

    start_date = fields.Date('Start Date', default=datetime.today())
    end_date = fields.Date('End Date', default=datetime.today())
    person_id = fields.Many2one('res.partner', string='Delivery Person', required=True,
                                copy=False)
    person_domain = fields.Char(compute="_compute_person_domain", readonly=True, store=False)

    @api.depends('person_id')
    def _compute_person_domain(self):
        for rec in self:
            person_list = []
            user_obj = self.env['res.users'].sudo().browse(self._uid)
            if user_obj.partner_id:
                if user_obj.has_group('access_rights_customization.group_delivery_operator') or user_obj.has_group(
                        'access_rights_customization.group_pickupandpackaging_operator'):
                    person_list.append(user_obj.partner_id.id)
                elif user_obj.has_group('picking_and_delivery_vendor.pickup_vendor_group') or user_obj.has_group(
                        'picking_and_delivery_vendor.delivery_vendor_group'):
                    person_ids = self.env['res.partner'].search(
                        [('commercial_partner_id', '=', user_obj.partner_id.commercial_partner_id.id),
                         ('active', '=', True)])
                    if person_ids:
                        for pids in person_ids:
                            person_list.append(pids.id)
                else:
                    person_ids = self.env['res.partner'].search(['|',('delivery_vendor', '=', True), ('picking_vendor', '=', True)])
                    if person_ids:
                        for vids in person_ids:
                            person_list.append(vids.id)

            rec.person_domain = json.dumps([('id', 'in', person_list)])

    def generate_order_report(self):
        vals = []
        person_data = {}

        records = self.env['dpr.delivery.result'].search([])

        if records:
            records.unlink()

        if self.person_id:
            person_data = self._calculate_delivery_dpr(self.person_id, self.start_date, self.end_date)

        for v_data in person_data:
            res = {
                'start_date': self.start_date,
                'end_date': self.end_date,
                'report_date': datetime.today(),
                'dpr_person_name': self.person_id.name,
                'dpr_picking_type': v_data.get("dpr_picking_type"),
                'dpr_status': v_data.get("dpr_status"),
                'dpr_order_number': v_data.get("dpr_order_number"),
                'dpr_reference': v_data.get("dpr_reference"),
                'dpr_picking_date': v_data.get("scheduled_date"),
            }

            vals.append(res)

        if vals:
            self.env['dpr.delivery.result'].create(vals)
            wizard_form = self.env.ref('dpr_delivery_result_tree', False)

            return {
                'name': 'Delivery Person Report',
                'type': 'ir.actions.act_window',
                'view_type': 'form',
                'view_mode': 'tree',
                'res_model': 'dpr.delivery.result',
                'views': [(wizard_form, 'tree')],
                # 'domain' : [('mp_seller_name','=', self.env.user.partner_id.name)],
                'target': 'current',
            }
        else:
            raise ValidationError(_("No records found."))

    def _calculate_delivery_dpr(self, vendor_id, start_date, end_date):
        for obj in vendor_id:
            if obj.picking_vendor == True and obj.delivery_vendor == False:
                query = '''
                    SELECT sp.scheduled_date,sp.name dpr_reference,sp.origin dpr_order_number,
                    spt.name dpr_picking_type,
                    CASE WHEN sp.state='done' THEN 'DONE'
                    WHEN sp.state ='delivering' THEN 'Delivering Now'
                    WHEN sp.state ='confirmed' THEN 'Waiting'
                    WHEN sp.state ='assigned' THEN 'Ready'
                    WHEN sp.state ='waiting' THEN 'Waiting Another Operation'
                    WHEN sp.state ='cancel' THEN 'Cancelled'
                    WHEN sp.state ='hold' THEN 'Hold'
                    WHEN sp.state ='draft' THEN 'Draft' END dpr_status,
                    sp.pick_date picking_date, pp.name dpr_pickup_person
                    FROM stock_picking sp 
                    INNER JOIN stock_picking_type spt ON spt.id=sp.picking_type_id                
                    INNER JOIN res_partner pp ON pp.id=sp.pickup_person_id               
                    WHERE 1=1
                    AND sp.scheduled_date BETWEEN %s AND %s
                    AND sp.pickup_person_id = %s
                    ORDER BY sp.id'''
                self.env.cr.execute(query, (start_date,end_date,obj.id,))
                query_res = self._cr.dictfetchall()
            elif obj.delivery_vendor == True and obj.picking_vendor == False:
                query = '''
                    SELECT sp.scheduled_date,sp.name dpr_reference,sp.origin dpr_order_number,
                    spt.name dpr_picking_type,
                    CASE WHEN sp.state='done' THEN 'DONE'
                    WHEN sp.state ='delivering' THEN 'Delivering Now'
                    WHEN sp.state ='confirmed' THEN 'Waiting'
                    WHEN sp.state ='assigned' THEN 'Ready'
                    WHEN sp.state ='waiting' THEN 'Waiting Another Operation'
                    WHEN sp.state ='cancel' THEN 'Cancelled'
                    WHEN sp.state ='hold' THEN 'Hold'
                    WHEN sp.state ='draft' THEN 'Draft' END dpr_status,
                    sp.pick_date picking_date, pp.name dpr_pickup_person
                    FROM stock_picking sp 
                    INNER JOIN stock_picking_type spt ON spt.id=sp.picking_type_id                
                    INNER JOIN res_partner pp ON pp.id=sp.pickup_person_id               
                    WHERE 1=1
                    AND sp.scheduled_date BETWEEN %s AND %s
                    AND sp.delivery_person_id = %s
                    ORDER BY sp.id'''
                self.env.cr.execute(query, (start_date, end_date, obj.id,))
                query_res = self._cr.dictfetchall()
            elif obj.delivery_vendor == True and obj.picking_vendor == True:
                query = '''
                    (SELECT sp.scheduled_date,sp.name dpr_reference,sp.origin dpr_order_number,
                    spt.name dpr_picking_type,
                    CASE WHEN sp.state='done' THEN 'DONE'
                    WHEN sp.state ='delivering' THEN 'Delivering Now'
                    WHEN sp.state ='confirmed' THEN 'Waiting'
                    WHEN sp.state ='assigned' THEN 'Ready'
                    WHEN sp.state ='waiting' THEN 'Waiting Another Operation'
                    WHEN sp.state ='cancel' THEN 'Cancelled'
                    WHEN sp.state ='hold' THEN 'Hold'
                    WHEN sp.state ='draft' THEN 'Draft' END dpr_status,
                    sp.pick_date picking_date, pp.name dpr_pickup_person
                    FROM stock_picking sp 
                    INNER JOIN stock_picking_type spt ON spt.id=sp.picking_type_id                
                    INNER JOIN res_partner pp ON pp.id=sp.pickup_person_id               
                    WHERE 1=1
                    AND sp.scheduled_date BETWEEN %s AND %s
                    AND sp.pickup_person_id = %s
                    ORDER BY sp.id)
                    UNION
                    (SELECT sp.scheduled_date,sp.name dpr_reference,sp.origin dpr_order_number,
                    spt.name dpr_picking_type,
                    CASE WHEN sp.state='done' THEN 'DONE'
                    WHEN sp.state ='delivering' THEN 'Delivering Now'
                    WHEN sp.state ='confirmed' THEN 'Waiting'
                    WHEN sp.state ='assigned' THEN 'Ready'
                    WHEN sp.state ='waiting' THEN 'Waiting Another Operation'
                    WHEN sp.state ='cancel' THEN 'Cancelled'
                    WHEN sp.state ='hold' THEN 'Hold'
                    WHEN sp.state ='draft' THEN 'Draft' END dpr_status,
                    sp.pick_date picking_date, pp.name dpr_pickup_person
                    FROM stock_picking sp 
                    INNER JOIN stock_picking_type spt ON spt.id=sp.picking_type_id                
                    INNER JOIN res_partner pp ON pp.id=sp.pickup_person_id               
                    WHERE 1=1
                    AND sp.scheduled_date BETWEEN %s AND %s
                    AND sp.delivery_person_id = %s
                    ORDER BY sp.id)'''
                self.env.cr.execute(query, (start_date, end_date, obj.id,start_date, end_date, obj.id))
                query_res = self._cr.dictfetchall()
            return query_res

class DPRDeliveryResult(models.TransientModel):
    _name = 'dpr.delivery.result'

    start_date = fields.Date('From Date')
    end_date = fields.Date('To Date')
    report_date = fields.Date('Report Date', default=datetime.today())

    dpr_person_name = fields.Char('Person Name')
    dpr_picking_type = fields.Char('Type')
    dpr_status = fields.Char('Status')

    dpr_order_number = fields.Char('Order Number')
    dpr_reference = fields.Char('Reference')
    dpr_picking_date = fields.Date('Pick Date')



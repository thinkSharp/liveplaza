# -*- coding: utf-8 -*-

from odoo import tools
from odoo import api, fields, models

class PickupReportWizard(models.TransientModel):
    _name = 'pickup.report.wizard'
    _description = 'Pickup Report Wizard'

    vendor_id = fields.Many2one('res.partner', string='Vendor')

    def get_report(self):
        pickup_records = self.env['picking.move'].search([('state', '=', 'draft')])
        data = {
            'doc_ids': pickup_records,
            'doc_model': 'pickup.report',
            'docs': pickup_records,
        }

    
        return self.env.ref('picking_and_delivery_vendor.report_pickup_move').report_action(self, data=data)


# class ReportPickupMove(models.AbstractModel):
#     _name = 'report.picking_and_delivery_vendor.report_pickup_move'

#     def prepare_report(self, docids, data=None):
#         pickup_records = self.env['pickup.report'].browse(docids)
#         doargs = {
#             'doc_ids': docids,
#             'doc_model': 'pickup.report',
#             'docs': pickup_records,
#             'data': data,
#         }

#         return doargs




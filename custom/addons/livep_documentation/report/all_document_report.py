# from odoo import api, fields, models

# class AllDocumentReport(models.Model):
#     _name = 'report.livep_documentation.report_webview_document'
#     _description = 'All Document Report'

#     @api.model
#     def _get_report_values(self, docids, data=None):
#         docs = self.env['create.documents'].search([])
#         return {
#             'docs': docs,
#         }
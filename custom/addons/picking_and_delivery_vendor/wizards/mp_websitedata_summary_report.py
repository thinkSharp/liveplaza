# -*- coding: utf-8 -*-

from odoo import api, fields, models, tools, _
from datetime import datetime

from odoo.exceptions import ValidationError,UserError, Warning

class MPWebsiteDataSummaryWizard(models.TransientModel):
    _name = 'mp.websitedata.summary.wizard'
    
    start_date = fields.Date('Start Date', default=datetime.today())
    end_date = fields.Date('End Date', default=datetime.today())
    report_type = fields.Selection([('buyers', 'Buyers'), ('sellers', 'Sellers'),
                                    ('products', 'Products'),('all', 'All')], string="Type", default="all")
    all_dates = fields.Boolean("All Dates", help="It will generate current data. No date filter for report.")
    
    def generate_report(self):
        vals = []
        
        records = self.env['mp.websitedata.summary.result'].search([])
        
        if records:
            records.unlink()
        
        if self.all_dates:
            seller_domain = [('active', '=', True), ('seller', '=', True), ('website_published', '=', True)]
        else:
            seller_domain = [('create_date', '>=', self.start_date), ('create_date', '<=', self.end_date), ('active', '=', True), 
                         ('seller', '=', True), ('website_published', '=', True)]
        
        if self.all_dates:
            product_domain = [('active', '=', True), ('status', '=', 'approved'), ('website_published', '=', True)]
        else:
            product_domain = [('create_date', '>=', self.start_date), ('create_date', '<=', self.end_date), ('active', '=', True), 
                         ('status', '=', 'approved'), ('website_published', '=', True)]
        
        if self.report_type == "buyers":
            if self.all_dates:
                self._cr.execute('''
                    SELECT id
                    FROM res_partner
                    WHERE 1=1
                    AND seller IS NOT TRUE AND employee IS NOT TRUE and picking_vendor IS NOT TRUE AND delivery_vendor IS NOT TRUE
                    AND is_company IS NOT TRUE AND township_id IS NOT NULL AND active = TRUE AND type='contact'
                    ORDER BY id desc
                ''')
                query_res = self._cr.dictfetchall()
            else:
                self._cr.execute('''
                    SELECT id
                    FROM res_partner
                    WHERE create_date >= %s and create_date <= %s
                    AND seller IS NOT TRUE AND employee IS NOT TRUE and picking_vendor IS NOT TRUE AND delivery_vendor IS NOT TRUE
                    AND is_company IS NOT TRUE AND township_id IS NOT NULL AND active = TRUE AND type='contact'
                    ORDER BY id desc
                ''', [self.start_date, self.end_date])
                query_res = self._cr.dictfetchall()
                                 
            res = {
                    'name': 'Active Buyers',
                    'start_date': self.start_date,
                    'end_date': self.end_date,
                    'active_product_count': 0.0,
                    'active_seller_count': 0.0,
                    'active_buyer_count': len(query_res),
                }        
            vals.append(res)
            
        elif self.report_type == "sellers":
            data_records = self.env['res.partner'].search(seller_domain, order='id desc')
            res = {
                    'name': 'Active Sellers',
                    'start_date': self.start_date,
                    'end_date': self.end_date,
                    'active_product_count': 0.0,
                    'active_buyer_count': 0.0,
                    'active_seller_count': len(data_records),
                }        
            vals.append(res)
        elif self.report_type == "products":
            data_records = self.env['product.template'].search(product_domain, order='id desc')
            res = {
                    'name': 'Active Products',
                    'start_date': self.start_date,
                    'end_date': self.end_date,
                    'active_seller_count': 0.0,
                    'active_buyer_count': 0.0,
                    'active_product_count': len(data_records),
                }        
            vals.append(res)
        elif self.report_type == "all":
            product_data_records = self.env['product.template'].search(product_domain, order='id desc')
            seller_data_records = self.env['res.partner'].search(seller_domain, order='id desc')
            
            if self.all_dates:
                self._cr.execute('''
                    SELECT id
                    FROM res_partner
                    WHERE 1=1
                    AND seller IS NOT TRUE AND employee IS NOT TRUE and picking_vendor IS NOT TRUE AND delivery_vendor IS NOT TRUE
                    AND is_company IS NOT TRUE AND township_id IS NOT NULL AND active = TRUE AND type='contact'
                    ORDER BY id desc
                ''')
                query_res = self._cr.dictfetchall()
            else:
                self._cr.execute('''
                    SELECT id
                    FROM res_partner
                    WHERE create_date >= %s and create_date <= %s
                    AND seller IS NOT TRUE AND employee IS NOT TRUE and picking_vendor IS NOT TRUE AND delivery_vendor IS NOT TRUE
                    AND is_company IS NOT TRUE AND township_id IS NOT NULL AND active = TRUE AND type='contact'
                    ORDER BY id desc
                ''', [self.start_date, self.end_date])
                query_res = self._cr.dictfetchall() 
                
            res = {
                    'name': 'Active Buyers/Sellers/Products',
                    'start_date': self.start_date,
                    'end_date': self.end_date,
                    'active_seller_count': len(seller_data_records),
                    'active_buyer_count': len(query_res),
                    'active_product_count': len(product_data_records),
                }        
            vals.append(res)
            
        if vals:
            self.env['mp.websitedata.summary.result'].create(vals)
            wizard_form = self.env.ref('mp_websitedata_summary_result_tree', False)
                
            return {
                'name': 'Website Data Summary Report',
                'type': 'ir.actions.act_window',
                'view_type': 'form',
                'view_mode': 'tree',
                'res_model': 'mp.websitedata.summary.result',
                'views': [(wizard_form, 'tree')],
                'target': 'current',
            }
        else:
            raise ValidationError(_("No records found."))


class MPWebsiteDataSummaryResult(models.TransientModel):
    _name = 'mp.websitedata.summary.result'
    
    name = fields.Char('Report Name')
    start_date = fields.Date('Start Date')
    end_date = fields.Date('End Date')

    active_product_count = fields.Float('Active Product Count')
    active_seller_count = fields.Float('Active Seller Count')
    active_buyer_count = fields.Float('Active Buyer Count')

    
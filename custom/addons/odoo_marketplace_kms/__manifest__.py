# -*- coding: utf-8 -*-

{
    'name': 'Seller Payment Report',
    'version': '1.0',
    'summary': 'Custom report for seller payment',
    'category': 'Extra Tools',
    'author': 'Kaung Moe Sat',
    'depends': ['odoo_marketplace'],
    'data': [
        'security/ir.model.access.csv',
        'view/seller_payment_report.xml',
        'view/commission_report.xml',
        'wizard/commission_report_wizard.xml',
    ], 
    'installable': True,
    'application': False,
    'auto_install': False,
}

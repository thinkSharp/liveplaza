# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'Liveplaza Documentation',
    'version': '1.0',
    'summary': 'Documentation',
    'sequence': -100,
    'description': "",
    'depends': ['base'],
    'category': 'Operations/Inventory',
    'demo': [],
    'data': [
        'security/ir.model.access.csv',
        'views/livep_doc.xml',
        'report/report_pdf_document.xml',
        'report/report_webview_document.xml',
        'report/report.xml',
    ],
    'qweb': [],
    'installable': True,
    'application': True,
    'auto_install': False,
}

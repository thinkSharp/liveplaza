# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'Documentations',
    'version': '13.0.0',
    'summary': 'Documentations',
    'description': "Documentation for Liveplaza user guides",
    'depends': [
        'website',
    ],
    'category': 'documents',
    'sequence': 20,
    'demo': [

    ],
    'data': [
        'views/documents.xml',
        'views/documents_web_view.xml',
        'views/layout.xml',
        'security/ir.model.access.csv',
    ],

    'qweb': ['static/src/xml/doc_template.xml'],
    'installable': True,
    'application': True,
    'auto_install': False,

}

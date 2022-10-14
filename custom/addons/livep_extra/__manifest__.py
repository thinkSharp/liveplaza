# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'LiveP Extra',
    'version': '1.1',
    'summary': 'LiveP Extra',
    'description': "",
    'depends': ['stock',
                'stock_account',
                'sale',
                'website_sale',
                'base', 
                'resource',
                'sale_stock',
                ],
    'category': 'Operations/Inventory',
    'sequence': 13,
    'demo': [

    ],
    'data': [
        #'security/ir.model.access.csv',
        #'views/res_config_settings_views.xml',
        'views/payment_views.xml',
        #'data/account_data.xml',
    ],

    'qweb': [

    ],
    'installable': True,
    'application': True,
    'auto_install': False,

}

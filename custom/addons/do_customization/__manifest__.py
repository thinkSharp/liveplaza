# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'DO Customization',
    'version': '1.1',
    'summary': 'DO Customization',
    'description': "",
    'depends': ['stock',
                'product',
                'odoo_marketplace',
                'stock_account', 
                'picking_and_delivery_vendor',
                'sale',
                'website_sale',
                'base', 
                'resource',
                'sale_stock','delivery',
                ],
    'category': 'Operations/Inventory',
    'sequence': 13,
    'demo': [

    ],
    'data': [
        #'security/stock_security.xml',
        #'security/ir.model.access.csv',
        'views/do_sale_order_view.xml',
        'views/stock_picking_views.xml',
        'views/templates.xml',
        'views/res_partner.xml',
    ],

    'qweb': [

    ],
    'installable': True,
    'application': True,
    'auto_install': False,

}

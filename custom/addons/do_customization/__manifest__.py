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
                'payment',
                ],
    'category': 'Operations/Inventory',
    'sequence': 13,
    'demo': [

    ],
    'data': [
        #'security/stock_security.xml',
        'security/ir.model.access.csv',
        'views/do_sale_order_view.xml',
        'views/stock_picking_views.xml',
        'views/templates.xml',
        'views/res_partner.xml',
        'views/sol_seller_view.xml',
        'views/faq.xml',
        'views/faq_web_view.xml',
        'views/create_seller_shop.xml',
        'views/portal_my_orders.xml',
        'views/checkout_preview.xml',
        'views/invoice_format.xml',
        'data/account_data.xml',
        'wizards/delivery_vendor_report_wizard_view.xml',
        'wizards/delivery_person_report_wizard_view.xml',
        'wizards/delivery_cod_payment_report_wizard_view.xml',
    ],

    'qweb': [

    ],
    'installable': True,
    'application': True,
    'auto_install': False,

}

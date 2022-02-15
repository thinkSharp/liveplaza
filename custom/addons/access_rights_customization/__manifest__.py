# -*- coding: utf-8 -*-
{
    'name': 'Access Rights Customization',
    'author': 'LivePlaza Technical Team',
    'version': '13.1.0',
    'summary': 'Access Rights Customization',
    'depends': ['base', 'account', 'sale', 'analytic', 'subscription_management', 'picking_and_delivery_vendor'],
    'data': [
            'security/ar_finance_group.xml',
            'security/ar_delivery_group.xml',
            'security/ar_customer_service_group.xml',
            'security/ar_pickupandpackaging_group.xml',
            'security/ir.model.access.csv'
            ],
    'installable': True,
    'auto_install': False,
    'category': 'Extra Tools',
}
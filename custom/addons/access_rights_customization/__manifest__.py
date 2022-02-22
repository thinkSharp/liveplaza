# -*- coding: utf-8 -*-
{
    'name': 'Access Rights Customization',
    'author': 'LivePlaza Technical Team',
    'version': '13.1.0',
    'summary': 'Access Rights Customization',
    'depends': ['base', 'account', 'sale', 'analytic', 'subscription_management', 'picking_and_delivery_vendor', 'im_livechat',
                'website_livechat', 'website', 'product', 'multi_product_request', 'marketplace_facebook_live_stream', 'mail',
                'odoo_marketplace', 'website_crm', 'stock'],
    'data': [
            'security/ar_finance_group.xml',
            'security/ar_delivery_group.xml',
            'security/ar_customer_service_group.xml',
            'security/ar_pickupandpackaging_group.xml',
            'security/ar_operation_group.xml',
            'security/ar_seller_tier_1_group.xml',
            'security/ar_seller_tier_2_group.xml',
            'security/ar_seller_tier_3_group.xml',
            'security/ir.model.access.csv'
            ],
    'installable': True,
    'auto_install': False,
    'category': 'Extra Tools',
}
# -*- coding: utf-8 -*- --

{
    'name' : 'Customizations by LiveP',
    'version' : '13.0.0.1',
    'summary' : 'The customizations made by liveplaza tech team.',
    'company' : 'LivePlaza',
    'depends' : [
                'base',
                'base_setup',
                'website_sale', 
                'odoo_marketplace', 
                'marketplace_facebook_live_stream'
                ],
    'data' : [
        'security/ir.model.access.csv',
        'views/seller_views.xml',
        'views/township_views.xml',
        'views/website_templates.xml',
        'views/delivery_carrier_views.xml',
        'views/sale_views.xml',
        'views/current_live_stream_inherit.xml',
        'views/seller_live_stream_inherit.xml',
        'views/checkout_template_inherit.xml',
        'views/setting_config_inherit.xml',
        'views/signup_form_inherit.xml',
        'data/data.xml'
    ],
    'installable' : True,
    'application' : False,
    'auto-install' : False,
}

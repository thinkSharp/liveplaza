{
    'name': 'Service Product',
    'version': '1.0',
     "depends": [
        'stock',
        'product',
        'odoo_marketplace',
        'website_sale',
         'base',
        'auth_signup',
        'sms_notification',
        'sale_management',
         'sale'
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/product_request_views.xml',
        # 'views/product_template_inherit.xml',
        'data/sequence.xml',
        'views/ticket.xml',
        'edi/service_code_to_customer.xml',
        'views/home.xml'
    ]

}


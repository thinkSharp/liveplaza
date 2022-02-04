{
    'name': 'Multi Product Request',
    'version': '1.0',
     "depends": [
        'stock',
        'product',
        'odoo_marketplace',
        'website_sale',
         'base',
        'auth_signup'
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/product_request_views.xml',
        'data/sequence.xml'
    ]
}


# -*- coding: utf-8 -*-

{
    "name":  "Custom Inventory Forms",
    "summary":  """Custom inventory forms for sellers""",
    "category":  "Website",
    "version":  "13.0.0",
    "sequence":  1,
    "author":  "Kaung Moe Sat",
    "depends": [
        'stock',
        'product',
        'odoo_marketplace',
        'website_sale',
        'custom_product_tabs'
    ],
    "data":  [
        'security/ir.model.access.csv',
        'security/security.xml',
        'data/ir_sequence_data.xml',
        'views/product_request_view.xml',
        'views/seller_view_inherit.xml',
        'wizard/product_variants_request_wiz.xml',
        'views/product_variants_request_view.xml',
        'views/setting.xml'
        

    ],
    # "images"               :  ['static/description/Banner.png'],
    "application":  False,
    "installable":  True,
}

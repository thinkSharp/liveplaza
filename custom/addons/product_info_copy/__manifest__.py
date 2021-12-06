# -*- coding: utf-8 -*-

{
    'name': 'Product Info Copy',
    'version': '13.1.0',
    'category': 'Website',
    'summary': 'Product Info Copy for Seller',
    'description': """
This module let the seller to copy their product info.
    """,
    'depends': ['odoo_marketplace'],
    'data': [
        'views/product_info_copy.xml',
    ],
    "external_dependencies": {"python": ['pyperclip']},
    'installable': True,
    'auto_install': False
}

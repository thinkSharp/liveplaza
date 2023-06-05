# -*- coding: utf-8 -*-
{
    'name': "celebrity_news",

    'summary': """
        Celebrity News Page""",

    'author': "LIVEPlaza",
    'website': "http://liveplaza.co",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/13.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'website'],

    # always loaded
    'data': [
        'views/templates.xml',
        'views/frontend_assets.xml',
    ],
}

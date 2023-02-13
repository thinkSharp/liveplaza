# -*- coding: utf-8 -*-
{
    'name': "Google Analytics 4",

    'summary': """
        Integration of Google Analytics 4 on odoo using Measurement ID""",

    'author': "LIVEPlaza",
    'website': "http://liveplaza.online",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/13.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Website',
    'version': '0.1',
    'application': True,

    # any module necessary for this one to work correctly
    'depends': ['website'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/res_config_views.xml',
        'views/templates.xml',
    ],
}

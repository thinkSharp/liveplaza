# -*- coding: utf-8 -*-
{
    'name': 'Two factor authentication',
    'version': '1.0',
    'category': 'Tools',
    'summary': """
         Stronger security for your Odoo account with 2-Factor Authentication""",
    'description': """
        Stronger security for your Odoo account with 2-Factor Authentication
    """,
    'author': 'Magenest',
    'license': 'LGPL-3',
    'depends': ['auth_signup'],
    'data': [
        'security/ir.model.access.csv',
        'security/security.xml',
        'views/res_users.xml',
        'views/view_2FA_auth.xml',
        'views/res_config_settings_views.xml',
        'views/check_login_fail_view.xml',
        'views/white_list_ip_view.xml',
        'views/templates.xml',
        'views/company_config.xml'
    ],
    'external_dependencies': {
        'python': ['pyotp', 'pyqrcode'],
    },
    'images': ['static/description/avatar_big.png'],
    'installable': True,
    'auto_install': False,
}

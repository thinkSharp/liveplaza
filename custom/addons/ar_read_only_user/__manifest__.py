# -*- coding: utf-8 -*-

{
    'name': 'Access Rights Read Only User Module',
    "author": "LivePlaza Technical Team",
    'version': '13.1.0',
    'summary': "Read only and limited access rights to user, limited write access to limited users and modules """,
    'depends': ['base','sale_management'],
    'data': [
            'security/user_read_only_group.xml',
            'security/ir.model.access.csv',
            'views/res_user_read_only.xml',
            ],
    'installable': True,
    'auto_install': False,
    'category': 'Extra Tools',
}

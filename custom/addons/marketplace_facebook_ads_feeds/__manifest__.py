# -*- coding: utf-8 -*-
#################################################################################
# Author      : Webkul Software Pvt. Ltd. (<https://webkul.com/>)
# Copyright(c): 2015-Present Webkul Software Pvt. Ltd.
# All Rights Reserved.
#
#
#
# This program is copyright property of the author mentioned above.
# You can`t redistribute it and/or modify it.
#
#
# You should have received a copy of the License along with this program.
# If not, see <https://store.webkul.com/license.html/>
#################################################################################
{
    'name': 'Marketplace Facebook Catalog Integration',
    'version': '1.0.0',
    'description': 'Marketplace Facebook Catalog Integration',
    'summary': 'Marketplace Facebook Catalog Integration',
    'author': 'Webkul Software Pvt. Ltd.',
    'website': 'store.webkul.com',
    'license': 'Other proprietary',
    'category': 'Website',
    'depends': [
        'odoo_marketplace',
        'facebook_ads_feeds'
    ],
    'data': [
        'security/ir.model.access.csv',
        'security/security.xml',
        'views/facebook_shop_view.xml'
    ],
    'auto_install': False,
    'application': True,
    'installable':True
    }
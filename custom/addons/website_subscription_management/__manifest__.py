# -*- coding: utf-8 -*-
#################################################################################
# Author      : Webkul Software Pvt. Ltd. (<https://webkul.com/>)
# Copyright(c): 2019-Present Webkul Software Pvt. Ltd.
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
    'name': "Website Subscription Management",
    'summary': """
        Website Subscription Management:The module facilitates the customers to purchase a subscription plan for products directly from the Odoo website""",
    'description': """
        website subscription : This module helps to purchase and manage the subscription plans.
    """,
    'author': "Webkul Software Pvt. Ltd.",
    'website': "https://store.webkul.com/",
    'category': 'Website',
    'version': '3.0.0',
    "license":  "Other proprietary",
    "live_test_url":  "http://odoodemo.webkul.com/?module=website_subscription_management&version=13.0&custom_url=/shop/",
    'depends': ['website_sale','subscription_management','mail','website_sale_comparison','website_sale_wishlist',],
    'data': [
        'security/ir.model.access.csv',
        'views/views.xml',
        'views/templates.xml',
    ],
    'demo': [
        'demo/demo.xml',
    ],
    "images": ['static/description/Banner.png'],
    "price": 60,
    "currency": 'EUR',
}

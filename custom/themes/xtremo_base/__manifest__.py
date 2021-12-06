
# -*- coding: utf-8 -*-
#################################################################################
#
#   Copyright (c) 2018-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>)
#   See LICENSE URL <https://store.webkul.com/license.html/> for full copyright and licensing details.
#################################################################################
{
    'name'          : "Xtremo Base",
    'description'   : 'Webkul odoo theme',
    'summary'       :  'Theme Xtremo consists wide range of things, such as font types, sizes, colors and other areas that affect the aesthetics of your site',
    'category'      : 'hidden',
    'author'        : 'Webkul Software Pvt. Ltd.',
    'sequence'      : 1,
    'live_test_url' : 'http://odoodemo.webkul.com/?module=theme_xtremo&custom_url=/',
    'version'       : '1.0.0',
    'website'       : 'https://store.webkul.com/Odoo-Theme-Xtremo.html',
    'depends'       : ['website_rating'],
    'data'          : [
                        'views/templates.xml',
                      ],
    'demo'          : [],
    'application'   : True,
    'installable'   : True,
    'auto_install'  : True,
    'currency'      : 'EUR',
    'pre_init_hook' : 'pre_init_check',
}

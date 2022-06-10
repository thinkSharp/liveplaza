# -*- coding: utf-8 -*-
#################################################################################
#
#   Copyright (c) 2018-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>)
#   See LICENSE URL <https://store.webkul.com/license.html/> for full copyright and licensing details.
#################################################################################
{
    'name': 'Xtremo Theme',
    'description': 'Webkul odoo theme',
    'summary' :  'Theme Xtremo consists wide range of things, such as font types, sizes, colors and other areas that affect the aesthetics of your site',
    'category': 'Theme/eCommerce',
    'author':'Webkul Software Pvt. Ltd.',
    'sequence': 1,
    'live_test_url' : 'https://xtremo_13.odoothemes.webkul.com',
    'version': '1.0.4',
    'website' : 'https://store.webkul.com/Odoo-Theme-Xtremo.html',
    'depends': [
        'website_sale',
        'website_theme_install',
        'website_sale_wishlist',
        'website_sale_comparison',
        'xtremo_base'
    ],
    'data': [
#         'static/src/xml/xtremo_dynamic_modal.xml',
        'view/frontend_assets.xml',
        'security/ir.model.access.csv',
        'view/customization.xml',
        # 'view/shop.xml',
        'view/product.xml',
        'view/cart.xml',
        'view/checkout.xml',
        'view/footer.xml',
        'view/header.xml',
        'view/xtremo_feature_view.xml',
        'view/snippet_template.xml',
        'view/snippet.xml',
        'view/xtremo_mega_menu_snippets.xml',
        'view/lazzy_loading.xml',
        'view/404.xml',
        
        # 'data/categories.xml',
        # 'data/products.template.xml',
        # 'data/product.multi.image.xml'
    ],
    'demo' : [],
    'images' : [
          'static/description/Banner.png',
          'static/description/xtremo_screenshot.jpg'
    ],
    'application': False,
    'license' :  'Other proprietary',
    'installable'  : True,
    'auto_install' : False,
    'currency' : 'EUR',
    'price' : 199,
    'pre_init_hook' : 'pre_init_check',

}

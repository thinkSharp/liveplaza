# -*- coding: utf-8 -*-
#################################################################################
# Author      : Webkul Software Pvt. Ltd. (<https://webkul.com/>)
# Copyright(c): 2015-Present Webkul Software Pvt. Ltd.
# License URL : https://store.webkul.com/license.html/
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
    "name" : "Odoo Facebook Messenger Chat",
    "summary" : "The Facebook Messenger chat widget will be visible in the odoo website.",
    "category" : "Website",
    "version" : "1.0.0",
    "sequence" : 1,
    "author" : "Webkul Software Pvt. Ltd.",
    "license" : "Other proprietary",
    "website" : "https://store.webkul.com/",
    "description" : """https://webkul.com/blog/""",
    "depends" : [
        'website',
    ],
    "data" : [
        "views/res_config_views.xml",
        "views/templates.xml",
    ],
    "demo" : [
    ],
    "images" : ['static/description/Banner.png'],
    "application" : True,
    "installable" : True,
    "auto_install" : False,
    "price" : 25,
    "currency" : "EUR",
    "pre_init_hook" : "pre_init_check",
}

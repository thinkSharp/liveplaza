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
  "name" : "Odoo MarketPlace with Facebook Live Stream",
  "summary" : """Sellers can promote their products with live stream videos from facebook.""",
  "category" : "Website",
  "version" : "1.0.1",
  "sequence" : 1,
  "author"  : "Webkul Software Pvt. Ltd.",
  "license" : "Other proprietary",
  "website" : "https://store.webkul.com/Odoo-Multi-Vendor-Marketplace.html",
  "description" :  """Odoo Multi Vendor Marketplace with facebook live stream for sellers to promote their products""",
  "depends" :  [
    "odoo_marketplace"
  ],
  "data" : [
    'security/livestream_security.xml',
    'security/ir.model.access.csv',
    'views/seller_live_stream_view.xml',
    'views/templates.xml',
    'views/inherit_website_templates.xml',
    'views/current_livestream_template.xml',
    'views/seller_profile_template.xml',
    'views/inherit_product_template.xml',
  ],
  "application" : True,
  "installable" : True,
  "auto_install" : False,
  "pre_init_hook" : "pre_init_check",
}

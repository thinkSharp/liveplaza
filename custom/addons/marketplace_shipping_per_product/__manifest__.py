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
  "name"                 :  "Odoo Marketplace Shipping Per Product",
  "summary"              :  "The module allows you to ship individual product through a separate shipping carrier in the same order.",
  "category"             :  "Website",
  "version"              :  "1.0.0",
  "sequence"             :  1,
  "author"               :  "Webkul Software Pvt. Ltd.",
  "license"              :  "Other proprietary",
  "website"              :  "https://store.webkul.com/Odoo-Marketplace-Shipping-Per-Product.html",
  "description"          :  """Odoo Marketplace Shipping Per Product
per-item shipping
Odoo Per product shipping
per -product shipping
Odoo per-item shipping rates
Shipping by item Odoo
Odoo Marketplace
Odoo multi vendor Marketplace
Multi seller marketplace
multi-vendor Marketplace""",
  "live_test_url"        :  "http://odoodemo.webkul.com/?module=marketplace_shipping_per_product",
  "depends"              :  [
                             'shipping_per_product',
                             'odoo_marketplace',
                            ],
  "data"                 :  ['views/inherit_mp_product_view.xml'],
  "images"               :  ['static/description/Banner.png'],
  "application"          :  True,
  "installable"          :  True,
  "auto_install"         :  False,
  "price"                :  25,
  "currency"             :  "EUR",
  "pre_init_hook"        :  "pre_init_check",
}

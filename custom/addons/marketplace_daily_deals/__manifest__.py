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
  "name"                 :  "Odoo Marketplace Daily Deals And Flash Sales",
  "summary"              :  """Odoo Marketplace Daily Deals And Flash Sales allows you to add Daily Deals And Flash Sales in your Odoo Marketplace""",
  "category"             :  "Website",
  "version"              :  "1.0.0",
  "sequence"             :  11,
  "author"               :  "Webkul Software Pvt. Ltd.",
  "license"              :  "Other proprietary",
  "website"              :  "https://store.webkul.com/Odoo-Marketplace-Daily-Deals.html",
  "description"          :  """Website Season sale
Odoo Weekend sale
Website daily deals
Website New deals
Latest deals
Discount sale
Odoo marketplace sale
Website sale
Odoo Marketplace
Odoo multi vendor Marketplace
Multi seller marketplace
multi-vendor Marketplace""",
  "live_test_url"        :  "http://odoodemo.webkul.com/?module=marketplace_daily_deals&lifetime=120&lout=1&custom_url=/",
  "depends"              :  [
                             'website_daily_deals',
                             'odoo_marketplace',
                            ],
  "data"                 :  [
                             'security/ir.model.access.csv',
                             'security/access_control_security.xml',
                             'views/seller_dashboard_daily_deals_view.xml',
                             'views/daily_deals_menu.xml',
                            ],
  "images"               :  ['static/description/Banner.png'],
  "application"          :  True,
  "installable"          :  True,
  "auto_install"         :  False,
  "price"                :  59,
  "currency"             :  "EUR",
  "pre_init_hook"        :  "pre_init_check",
}
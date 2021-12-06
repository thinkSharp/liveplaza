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
  "name"                 :  "Theme Xtremo Marketplace",
  "summary"              :  """Theme Xtremo Marketplace consists wide range of things, such as font types, sizes, colors and other areas that affect the aesthetics of your site""",
  "category"             :  "Theme/eCommerce",
  "version"              :  "1.0.3",
  "sequence"             :  1,
  "author"               :  "Webkul Software Pvt. Ltd.",
  "license"              :  "Other proprietary",
  "website"              :  "https://store.webkul.com/odoo-theme-xtremo-marketplace.html",
  "description"          :  """Theme Xtremo Marketplace. This Theme is depenedent on theme xtremo and odoo multivendor marketplace, this is aplicable for website only.""",
  "live_test_url"        :  "https://marketplace_xtremo_13.odoothemes.webkul.com",
  "depends"              :  [
                             'odoo_marketplace',
                             'theme_xtremo',
                            ],
  "data"                 :  ['view/frontend_assets.xml'],
  "images"               :  [
                             'static/description/Banner.png',
                             'static/description/xtremo_screenshot.png',
                            ],
  "application"          :  False,
  "installable"          :  True,
  "auto_install"         :  False,
  "price"                :  51,
  "currency"             :  "USD",
  "pre_init_hook"        :  "pre_init_check",
}
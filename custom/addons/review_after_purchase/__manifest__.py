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
  "name"                 :  "Website: Product Review After Purchase",
  "summary"              :  "Odoo Website Product Review After Purchase allows you to view all the ratings and feedbacks in the Odoo. Moreover, the user can also publish/unpublish a review on the website.",
  "category"             :  "Website",
  "version"              :  "1.0.2",
  "sequence"             :  1,
  "author"               :  "Webkul Software Pvt. Ltd.",
  "license"              :  "Other proprietary",
  "website"              :  "https://store.webkul.com/Odoo-Website-Product-Review-After-Purchase.html#",
  "description"          :  """Manage review for products after purchase
Odoo Website Product Review After Purchase
Ask for Product Review After Purchase
Product Review After Purchase Odoo Website 
How to Ask Customers for Reviews
How to Ask Customers to Leave a Product Review
Ask for review
Product Review request
Product Review After Purchase request in Odoo
Ask for Rate and Review
Requesting Review""",
  "live_test_url"        :  "http://odoodemo.webkul.com/?module=review_after_purchase",
  "depends"              :  [
                             'wk_review',
                             'website_webkul_addons',
                            ],
  "data"                 :  [
                             'security/ir.model.access.csv',
                             'data/cron.xml',
                             'data/edi.xml',
                             'views/website_webkul_addons.xml',
                             'views/res_config_view.xml',
                             'data/review_after_purchase_demo.xml',
                            ],
  "images"               :  ['static/description/Banner.png'],
  "application"          :  True,
  "installable"          :  True,
  "auto_install"         :  False,
  "price"                :  36,
  "currency"             :  "EUR",
  "pre_init_hook"        :  "pre_init_check",
}

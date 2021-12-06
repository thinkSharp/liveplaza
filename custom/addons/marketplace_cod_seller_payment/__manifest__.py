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
  "name"                 :  "Odoo Marketplace Cash On Delivery (COD)",
  "summary"              :  """This module allows admin to manage seller payment for COD orders.""",
  "category"             :  "Website",
  "version"              :  "1.0.0",
  "sequence"             :  1,
  "author"               :  "Webkul Software Pvt. Ltd.",
  "license"              :  "Other proprietary",
  "website"              :  "https://store.webkul.com/Odoo-Marketplace-Cash-On-Delivery-COD.html",
  "description"          :  """Odoo Marketplace Cash On Delivery (COD), Cash on delivery, COD""",
  "live_test_url"        :  "http://odoodemo.webkul.com/?module=marketplace_cod_seller_payment&version=13.0&lifetime=120&lout=1&custom_url=/",
  "depends"              :  [
                             'odoo_marketplace',
                             'payment_cash_on_delivery',
                            ],
  "data"                 :  ['wizard/inherit_seller_payment_wizard.xml'],
  "images"               :  ['static/description/Banner.png'],
  "application"          :  True,
  "installable"          :  True,
  "auto_install"         :  False,
  "price"                :  49,
  "currency"             :  "USD",
  "pre_init_hook"        :  "pre_init_check",
}
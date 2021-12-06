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
  "name"                 :  "Website Cash On Delivery",
  "summary"              :  """Website Cash On Delivery allows to add the option to pay for the order once the delivery is done.""",
  "category"             :  "Website",
  "version"              :  "2.1.0",
  "sequence"             :  1,
  "author"               :  "Webkul Software Pvt. Ltd.",
  "license"              :  "Other proprietary",
  "maintainer"           :  "Prakash Kumar",
  "website"              :  "https://store.webkul.com/Odoo-Website-COD-Payment-Acquirer.html",
  "description"          :  """Odoo Website Cash On Delivery
                                Website Cash On Delivery
                                Cash On Delivery
                                Pay On Delivery
                                Pay Money After Delivery
                                Pay after Delivery
                                COD in Odoo Website
                                COD
                                Supporting Cash On Delivery
                                Odoo COD
                                Cash On Delivery Payment Option
                                COD Payment Method""",
  "depends"              :  [
                             'payment',
                             'website_sale_management',
                             'stock',
                            ],
  "data"                 :  [
                             'views/template.xml',
                             'views/payment_cash_on_delivery.xml',
                             'data/cash_on_delivery.xml',
                             'security/ir.model.access.csv',
                            ],
  "images"               :  ['static/description/Banner.png'],
  "application"          :  True,
  "installable"          :  True,
  "price"                :  49.0,
  "currency"             :  "EUR",
  "pre_init_hook"        :  "pre_init_check",
  "post_init_hook"       :  "create_missing_journal_for_acquirers",
}

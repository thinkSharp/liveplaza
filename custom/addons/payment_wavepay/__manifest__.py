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
  "name"                 :  "Website WavePay  Payment Acquirer",
  "summary"              :  """Website WavePay  Payment Acquirer""",
  "category"             :  "Accounting",
  "version"              :  "1.0.0",
  "sequence"             :  1,
  "author"               :  "Webkul Software Pvt. Ltd.",
  "license"              :  "Other proprietary",
  "website"              :  "https://store.webkul.com/",
  "description"          :  """Payment WavePay""",
  "live_test_url"        :  "http://odoodemo.webkul.com/?module=payment_wavepay",
  "depends"              :  ['payment'],
  "data"                 :  [
                             'views/payment_views.xml',
                             'views/payment_wavepay_templates.xml',
                             'data/payment_acquirer_data.xml'
                            ],
  "images"               :  ['static/description/Banner.png'],
  "application"          :  True,
  "installable"          :  True,
  "price"                :  69,
  "currency"             :  "EUR",
  "pre_init_hook"        :  "pre_init_check",
  "post_init_hook"       :  "create_missing_journal_for_acquirers",
}

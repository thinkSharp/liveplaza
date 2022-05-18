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
  "name"                 :  "Redis Session Store",
  "summary"              :  """This module allows you to store the session in Redis in spite of in Filesystem in werkzeug.""",
  "category"             :  "Extra Tools",
  "version"              :  "1.0.0",
  "author"               :  "Webkul Software Pvt. Ltd.",
  "license"              :  "Other proprietary",
  "website"              :  "",
  "description"          :  """Allows you to store the session in redis inspite of werkzeug filestorage,Redis,Session""",
  "depends"              :  [
                             'base',
                             'base_setup',
                            ],
  "data"                 :  ['views/res_config.xml'],
  "css"                  :  [],
  "js"                   :  [],
  "images"               :  ['static/description/Banner.png'],
  "application"          :  True,
  "installable"          :  True,
  "auto_install"         :  True,
  "price"                :  69,
  "currency"             :  "USD",
  "external_dependencies":  {'python': ['redis']},
}
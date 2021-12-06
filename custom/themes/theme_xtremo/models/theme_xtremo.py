# -*- coding: utf-8 -*-
#################################################################################
#
#   Copyright (c) 2018-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>)
#   See LICENSE URL <https://store.webkul.com/license.html/> for full copyright and licensing details.
#################################################################################
from odoo import models
import logging
_log = logging.getLogger(__name__)

class ThemeXtremo(models.AbstractModel):
    _inherit = 'theme.utils'

    def _theme_xtremo_post_copy(self, mod):
        self.disable_view('website_theme_install.customize_modal')

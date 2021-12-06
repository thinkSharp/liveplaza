# -*- coding: utf-8 -*-
#################################################################################
# Author      : Webkul Software Pvt. Ltd. (<https://webkul.com/>)
# Copyright(c): 2015-Present Webkul Software Pvt. Ltd.
# License URL : https://store.webkul.com/license.html/
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

from odoo import models, fields, api, _
import logging
_logger = logging.getLogger(__name__)


class IrUiMenu(models.Model):
    _inherit = "ir.ui.menu"

    
    def hide_mp_menus_to_user(self, menu_data):
        """ Return the ids of the menu items hide to the user. """
        menu_ids = super(IrUiMenu, self).hide_mp_menus_to_user(menu_data)
        menu_ids = menu_ids if menu_ids else []

        officer_group = self.env['ir.model.data'].get_object_reference(
            'odoo_marketplace', 'marketplace_officer_group')[1]
        groups_ids = self.env.user.sudo().groups_id.ids
        if officer_group in groups_ids:
            try:
                menu_ids.extend((self.env.ref('marketplace_cod_seller_payment.wk_pay_to_admin_menu').id,))
            except Exception as e:
                pass
        return menu_ids

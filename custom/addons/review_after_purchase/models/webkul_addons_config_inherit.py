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
from odoo import api, fields, models, _


class WebkulWebsiteAddons(models.TransientModel):
    _inherit = 'webkul.website.addons'


    def get_module_review_after_purchase_view(self):
        ids = self.env['website.sale.review.config.settings'].search([])
        imd = self.env['ir.model.data']
        action = imd.xmlid_to_object('review_after_purchase.action_website_sale_review')
        list_view_id = imd.xmlid_to_res_id('review_after_purchase.view_wk_website_sale_review_tree')
        form_view_id = imd.xmlid_to_res_id('review_after_purchase.wk_website_sale_review')

        result = {
            'name': action.name,
            'help': action.help,
            'type': action.type,
            'views': [[list_view_id, 'tree'], [form_view_id, 'form']],
            'target': action.target,
            'context': action.context,
            'res_model': action.res_model,
        }
        return result

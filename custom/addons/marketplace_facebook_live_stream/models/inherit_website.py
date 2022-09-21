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

from odoo import api, fields, models
import logging
_logger = logging.getLogger(__name__)

class Website(models.Model):
    _inherit = 'website'

    def _get_seller_live_streams(self, view_name, seller_id=False, product_id=False):
        domain = [('live_stream_url','!=',False)]
        limit = 100
        live_stream_ids = False
        if view_name == 'seller_profile_page':
            domain.append(('publish_on_seller_profile','=',True))
            domain.append(('seller_id','=', int(seller_id)))
            limit = 10
            live_stream_ids = self.env["seller.live.stream"].search(domain, order='website_published desc', limit=limit)
        elif view_name == 'seller_shop_page':
            domain.append(('publish_on_seller_shop','=',True))
            domain.append(('website_published','!=',False))
            domain.append(('seller_id','=', int(seller_id)))
            live_stream_ids = self.env["seller.live.stream"].search(domain, order='live_stream_datetime desc', limit=limit)
        elif view_name == 'seller_shop_list_page':
            domain.append(('publish_on_seller_shop','=',True))
            domain.append(('website_published','!=',False))
            live_stream_ids = self.env["seller.live.stream"].search(domain, order='live_stream_datetime desc', limit=limit)
        elif view_name == 'mp_product_template':
            domain.append(('promoted_product_ids','in',product_id))
            domain.append(('website_published','!=',False))
            domain.append(('seller_id','=', int(seller_id)))
            live_stream_ids = self.env["seller.live.stream"].search(domain, order='live_stream_datetime desc', limit=limit)
        else:
            domain.append(('publish_on_shop','=',True))
            domain.append(('website_published','!=',False))
            live_stream_ids = self.env["seller.live.stream"].search(domain, order='live_stream_datetime desc')
        return live_stream_ids


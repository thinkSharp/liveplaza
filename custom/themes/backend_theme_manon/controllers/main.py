# -*- coding: utf-8 -*-
#################################################################################
#
#    Copyright (c) 2015-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>)
#
#################################################################################
import logging

from odoo import http
from odoo.http import request, route

_logger = logging.getLogger(__name__)

class WkTheme(http.Controller):

	@http.route(['/manon/theme_customize'], type='json', auth="public", website=True)
	def manon_theme_customize(self, get_bundle=False):
		if get_bundle:
			context = dict(request.context)
			return {
				'web.assets_backend': request.env["ir.qweb"].with_context(website_id=False)._get_asset_link_urls('web.assets_backend', options=context),
			}

		return True

	@http.route(['/theme/manon/make_scss_custo'], type='json', auth='user', website=True)
	def manon_make_scss_custo(self, url, values, style_type, **kw):
		request.env['web_editor.assets'].make_scss_customization_backend(url, values, style_type, **kw)
		return True
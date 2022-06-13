# -*- coding: utf-8 -*-
#################################################################################
##    Copyright (c) 2019-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>)
#    You should have received a copy of the License along with this program.
#    If not, see <https://store.webkul.com/license.html/>
#################################################################################

from odoo import api, fields, models
from datetime import datetime, timedelta, date
from dateutil.relativedelta import relativedelta
from odoo.exceptions import UserError

class ProductPricelist(models.Model):
	_inherit = "product.pricelist"

	def unlink(self):
		if self.name == "Deals Dummy Pricelist":
			raise UserError('This Pricelist Can Not be deleted as this is used by website daily deals Module.')
		else:
			return super(ProductPricelist , self).unlink();

class ProductPricelistItem(models.Model):
	_inherit = "product.pricelist.item"

	website_deals_m2o = fields.Many2one('website.deals', 'Corresponding Deal', help="My Deals", ondelete="cascade")
	actual_price = fields.Float(related ='product_tmpl_id.list_price',string='Actual Price', store=True)
	discounted_price = fields.Float('Discounted Price',default=0.0)
	website_size_x = fields.Integer('Size X',default=2)
	website_size_y = fields.Integer('Size Y',default=2)
	deal_applied_on = fields.Selection([('1_product', 'Product'),('0_product_variant', 'Product Variant')], "Apply On", default=False, required=True, help='Pricelist Item applicable on selected option')


	@api.onchange('deal_applied_on')
	@api.depends('deal_applied_on' )
	def onchange_deal_applied_on(self):
		self.applied_on = self.deal_applied_on
		self.pricelist_id = self.website_deals_m2o.deal_pricelist
		self.min_quantity = 1


class WebsiteDeals(models.Model):
	_name = 'website.deals'
	_description = 'Website Deals'
	_order = "id desc"

	@api.model
	def _get_default_pricelist(self):
		irDefault = self.env['ir.default'].sudo()
		deal_pricelist = irDefault.get('website.daily.deals.conf', 'deal_pricelist')
		return deal_pricelist

	name = fields.Char(string = 'Name', required=True)
	title = fields.Char(string = 'Title', required=True, help="title of the deal to show in website",default="Get a heavy discount on this season")
	show_title = fields.Boolean('Show Title In Website', help="the title will be displayed in the website and it is displayed only if 'What to Display in Website = Products Only'")
	description = fields.Text(string = 'Description' , help="description of the deal to show in website")
	state = fields.Selection([('draft','Draft'),('validated','In Progress'),('expired','Expired'),('cancel','Cancelled')],'State', default='draft')
	deal_pricelist = fields.Many2one('product.pricelist','Pricelist',required=True,default=_get_default_pricelist)
	overide_config = fields.Boolean('Override Default Configuration')

	start_date = fields.Datetime('Start Date', required=True, default=datetime.now()+ timedelta(days=-1))
	end_date = fields.Datetime('End Date', required=True, default=datetime.now() + timedelta(days=1))

	banner = fields.Binary('Banner', required=False)
	pricelist_items  = fields.One2many(comodel_name = 'product.pricelist.item', inverse_name ='website_deals_m2o' ,string='Products')
	display_products_as = fields.Selection([('grid','Grid'),('slider','Slider')],'How to display Products in Website', default='grid', help="choose how to display the produts in website.")
	item_to_show = fields.Selection([('banner_only','Banner Only'),('products_only','Products Only'), ('both','Both')],'What to Display in Website', default='both', help="choose what you want to display in website.")

	show_message_before_expiry = fields.Boolean('Show Message before Expiry',help="Do you want to show a message before the expiry date of the deal, if yes then set this true.")
	message_before_expiry = fields.Char('Message before Expiry', help="The message you want to show in the website when deal is about to expire.",default='Hurry Up!!! This deal is about to expire.')
	interval_before = fields.Integer('Time interval before to display message' , help="How much time before the expiry date you want to display the message.",default=1)
	unit_of_time = fields.Selection([('minutes','Minutes'),('hours','Hours'),('days','Days'),('weeks','Weeks')],'Time Unit',required=True, default='hours')

	show_message_after_expiry = fields.Boolean('Show Message After Expiry', help="Do you want to show the message after the expiry date of the deal.")
	message_after_expiry = fields.Char('Message After Expiry', help="The message you want to show in the website when deal is expired.",default='Opps!! This deal has been expired.')
	d_state_after_expire = fields.Selection([('blur','Blur'),('delete','Delete')],'What to do with deal after Expiry', default='blur', help="What do you want to do with deal after expiration.Either you can blur the deals in website or delete a deal from website")
	display_on_homepage = fields.Boolean(string='Display on Homepage', default=False)



	@api.model
	def create(self,vals):
		if not vals.get('banner'):
			raise UserError('No banner chosen, please choose a banner before saving.')
		return super(WebsiteDeals , self).create(vals)

	@api.model
	def _update_deal_items(self):
		pricelist = self.deal_pricelist
		if pricelist and self.state=='validated':
			for item in self.pricelist_items:
				item.pricelist_id = pricelist.id
				if item.product_tmpl_id:
					price = pricelist.get_product_price(item.product_tmpl_id,1,None)

				elif item.product_id:
					price = pricelist.get_product_price(item.product_id,1,None)
				else:
					price = 0.0
				item.discounted_price = price
		else:
			for item in self.pricelist_items:
				item.pricelist_id = self.env.ref("website_daily_deals.wk_deals_dummy_pricelist")

	@api.onchange('interval_before')
	def onchange_deal_interval_before(self):
		if self.interval_before == 0:
			self.interval_before = 1

	@api.onchange('deal_pricelist','start_date','end_date','overide_config','pricelist_items')
	def onchange_deal_config(self):
		self.set_to_draft()

	def set_to_draft(self):
		self.state = 'draft'
		self._update_deal_items()

	def set_to_expired(self):
		self.state = 'expired'
		self._update_deal_items()


	def button_validate_the_deal(self):
		start_date = self.start_date
		end_date = self.end_date
		if start_date > end_date:
			raise UserError('End date can not be earlier than start date.')
		elif end_date > datetime.now() :
			self.state = 'validated'
			self._update_deal_items()
		else:
			self.set_to_expired()


	@api.model
	def cancel_deal(self):
		self.state = 'cancel'
		self._update_deal_items()

	@api.model
	def get_valid_deals(self):
		return self.search(['|',('state','=','validated'),('state','=','expired')]).sorted(lambda d:d.state=="expired")

	@api.model
	def get_page_header(self):
		irDefault = self.env['ir.default'].sudo()
		show_header = irDefault.get('website.daily.deals.conf', 'show_page_header')
		return show_header and irDefault.get('website.daily.deals.conf', 'page_header_text')

	@api.model
	def is_deal_banner_shown(self):
		if self.overide_config:
			return self.item_to_show == 'banner_only' or self.item_to_show == 'both'
		else:
			config_value = self.env['ir.default'].sudo().get('website.daily.deals.conf', 'item_to_show')
			return config_value == 'banner_only' or config_value == 'both'
		return False

	# @api.model
	# def button_apply_this_pricelist(self,*args):
	# 	msg = "By applying this pricelist the currently applied pricelist of website will be removed and this pricelist will be active on current website."
	# 	return self.show_msg_wizard(msg)


	def show_msg_wizard(self, msg):
		res_id=self.env['deal.wizard.message'].create({'msg':msg})
		modal =  {
                'domain': "[]",
                'name': 'Warning',
                'view_type': 'form',
                'view_mode': 'form',
                'res_model': 'deal.wizard.message',
                'type': 'ir.actions.act_window',
                # 'context': {'feature_id': feature.id},
                'res_id':res_id.id,
                'view_id': self.env.ref('website_daily_deals.website_deal_wizard_pricelist_warning_form_view').id,
                'target': 'new',
        }
		return modal


	@api.model
	def is_deal_product_shown(self):
		if self.overide_config:
			return self.item_to_show == 'products_only' or self.item_to_show == 'both'
		else:
			config_value = self.env['ir.default'].sudo().get('website.daily.deals.conf', 'item_to_show')
			return config_value == 'products_only' or config_value == 'both'
		return False

	@api.model
	def get_display_products_as(self):
		if self.overide_config:
			return self.display_products_as
		else:
			config_value = self.env['ir.default'].sudo().get('website.daily.deals.conf', 'display_products_as')
			return config_value
		return "grid"

	@api.model
	def state_after_expiration(self):
		if self.overide_config:
			return self.state =='expired' and  self.d_state_after_expire
		else:
			config_value = self.env['ir.default'].sudo().get('website.daily.deals.conf', 'd_state_after_expire')
			return self.state =='expired' and config_value and 'blur'
		return False


	@api.model
	def get_message_before_expiry_and_offset(self):
		message = False
		td = False
		if self.state=="validated":
			if self.overide_config:
				if self.show_message_before_expiry:
					message =  self.message_before_expiry
					interval =  self.interval_before
					unit 	=  self.unit_of_time
					td = self.get_time_delta(interval,unit)
			else:
				IrDefault = self.env['ir.default'].sudo()
				if IrDefault.get('website.daily.deals.conf', 'show_message_before_expiry'):
					message = IrDefault.get('website.daily.deals.conf', 'message_before_expiry')
					interval = IrDefault.get('website.daily.deals.conf', 'show_message_before_expiry')
					unit = IrDefault.get('website.daily.deals.conf', 'show_message_before_expiry')
					td = self.get_time_delta(interval,unit)

		return {'message':message,'offset':td and self.end_date - td }
	@api.model
	def get_time_delta(self,interval,unit):
		if interval and unit:
			if unit=="minutes":
				td = timedelta(minutes=int(interval))
			elif unit=="hours":
				td = timedelta(hours=int(interval))
			elif unit=="days":
				td = timedelta(days=int(interval))
			elif unit=="weeks":
				td = timedelta(weeks=int(interval))
			elif unit=="months":
				td = timedelta(months=int(interval))
			else:
				td = timedelta(hours=1)

			return td
		return False

	@api.model
	def get_message_after_expiry(self):
		message = False
		if self.state=="expired":
			if self.overide_config:
				message =  self.show_message_after_expiry and self.message_after_expiry
			else:
				IrDefault = self.env['ir.default'].sudo()
				message = IrDefault.get('website.daily.deals.conf', 'show_message_after_expiry') and IrDefault.get('website.daily.deals.conf', 'message_after_expiry')
		return message

	# method for frontend contollers

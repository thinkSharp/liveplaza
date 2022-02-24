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
from datetime import datetime, timedelta
from odoo.exceptions import UserError
import logging, re
_logger = logging.getLogger(__name__)

class SellerLiveStream(models.Model):
    _name = "seller.live.stream"
    _desc = "Seller Live Stream"

    @api.model
    def _set_seller_id(self):
        user_obj = self.env['res.users'].sudo().browse(self._uid)
        if user_obj.partner_id and user_obj.partner_id.seller:
            return user_obj.partner_id.id
        return self.env['res.partner']

    name = fields.Char("Name", copy=True)
    host = fields.Selection(
        [('facebook', 'Facebook'), ('youtube', 'Youtube'), ('tiktok', 'Tiktok'), ('instagram', 'Instagram'), ('twitter', 'Twitter'),
         ('twitch', 'Twitch'), ('Weibo', 'Weibo')], string='Host', store=True)
    live_stream_url = fields.Char(string="Live Stream Url", copy=False, required=True)
    domain = fields.Char(string='Domain', store=True)
    embed_url = fields.Char(string="Embed Stream Url", copy=False, default="")
    description = fields.Text("Description")
    live_stream_datetime = fields.Datetime("Date and time of live stream", copy=False)
    start_stream_datetime = fields.Datetime("Start Date and time of live stream", copy=False)
    end_stream_datetime = fields.Datetime("End Date and time of live stream", copy=False)
    publish_on_shop = fields.Boolean("Shop Page", copy=False)
    publish_on_seller_shop = fields.Boolean("Seller Shop Page", copy=False)
    publish_on_seller_profile = fields.Boolean("Seller Profile Page", copy=False)
    website_published = fields.Boolean('Available on the website', copy=False, default=False)
    seller_id = fields.Many2one("res.partner", string="Seller", default=_set_seller_id, domain=[('seller', '=', True)], copy=True)
    promoted_product_ids = fields.Many2many(
        "product.template",
        string= "Products Promoted",
        help="select a set of products that it is going to promote on that live stream",
        required=True,
        copy=False,
        # domain = lambda self: [('marketplace_seller_id','in',self.env['seller.live.stream'].compute_login_userid()),('status','=','approved')],
    )
    live_stream_banner = fields.Binary(string="Live Stream Banner",help="""
    Add Banner to show on stream.
    """)

    def compute_login_userid(self):
        login_ids = []
        seller_group = self.env['ir.model.data'].get_object_reference(
            'odoo_marketplace', 'marketplace_seller_group')[1]
        officer_group = self.env['ir.model.data'].get_object_reference(
            'odoo_marketplace', 'marketplace_officer_group')[1]
        groups_ids = self.env.user.sudo().groups_id.ids
        if seller_group in groups_ids and officer_group not in groups_ids:
            login_ids.append(self.env.user.sudo().partner_id.id)
            return login_ids
        elif seller_group in groups_ids and officer_group in groups_ids:
            obj = self.env['res.partner'].search([('seller','=',True)])
            for rec in obj:
                login_ids.append(rec.id)
            return login_ids

    @api.onchange("live_stream_url")
    def update_live_stream_datetime(self):
        for rec in self:
            if rec.live_stream_url:
                rec.live_stream_datetime = fields.Datetime.now()

    @api.onchange("publish_on_shop","publish_on_seller_shop","publish_on_seller_profile")
    def check_if_website_published(self):
        for rec in self:
            if rec.website_published and not rec.publish_on_shop and not rec.publish_on_seller_shop and not rec.publish_on_seller_profile:
                rec.website_published = False


    def check_duplicate_views(self,vals=False):
        if vals:
            publish_on_shop = vals.get('publish_on_shop')
            publish_on_seller_shop = vals.get('publish_on_seller_shop')
            publish_on_seller_profile = vals.get('publish_on_seller_profile')
            seller_id = vals.get('seller_id')  or self.seller_id.id
        else:
            publish_on_shop = self.publish_on_shop
            publish_on_seller_shop = self.publish_on_seller_shop
            publish_on_seller_profile = self.publish_on_seller_profile
            seller_id = self.seller_id.id
        if publish_on_seller_shop or publish_on_seller_profile or publish_on_shop:
            records = self.env['seller.live.stream'].search([('id','!=',self.id),('seller_id','=',seller_id),('website_published','=',True)])
        else:
            return

    @api.onchange("seller_id")
    def update_promoted_product_ids(self):
        for rec in self:
            if rec.seller_id:
                if rec.promoted_product_ids:
                    rec.promoted_product_ids = False
                return {'domain': {'promoted_product_ids': [('marketplace_seller_id','=',rec.seller_id.id),('status','=','approved'),('marketplace_seller_id','!=',False)]}}
            else:
                rec.promoted_product_ids = False
                return {'domain': {'promoted_product_ids': [('marketplace_seller_id','in',self.env['seller.live.stream'].compute_login_userid()),('status','=','approved'),('marketplace_seller_id','!=',False)]}}

    def write(self, vals):
        if self.website_published:
            self.check_duplicate_views(vals)
        res = super(SellerLiveStream, self).write(vals)
        return res

    def toggle_website_published(self):
        for record in self:
            if record.website_published:
                record.website_published = False
            else:
                if not (record.publish_on_seller_profile or record.publish_on_seller_shop or record.publish_on_shop ):
                    raise UserError(_('Please select any one publish option where the stream is to be published'))
                if not self.live_stream_url:
                    raise UserError(_('Please enter the live stream url to publish'))
                try:
                    self.check_duplicate_views()
                except UserError as e:
                    record.website_published = False
                    raise(e)
                else:
                    record.live_stream_datetime = fields.Datetime.now()
                    record.website_published = True

    @api.onchange('live_stream_url')
    def set_embed_url(self):
        if self.live_stream_url:
            video_url = self.live_stream_url
            # Regex for few of the widely used video hosting services
            ytRegex = r'.*youtube.*v=(.*)'
            tkRegex = r'.*tiktok.com*/.*/.*/(.*)'
            igRegex = r'.*instagram.*'
            twitterRegex = r'.*twitter.*'
            twitchRegex = r'.*twitch.tv/(.*)'
            weiboRegex = r'.*weibo.*'
            facebookRegex = r'.*f.*watch.*'

            ytMatch = re.search(ytRegex, video_url)
            tkMatch = re.search(tkRegex, video_url)
            igMatch = re.search(igRegex, video_url)
            twitterMatch = re.search(twitterRegex, video_url)
            twitchMatch = re.search(twitchRegex, video_url)
            weiboMatch = re.search(weiboRegex, video_url)
            facebookMatch = re.search(facebookRegex, video_url)

            if facebookMatch:
                self.host = 'facebook'
                embedUrl = ''

            elif ytMatch:
                self.host ='youtube'
                embedUrl = 'https://www.youtube.com/embed/{}'.format(ytMatch.groups()[0])


            elif tkMatch:
                self.host = 'tiktok'
                embedUrl = tkMatch.groups()[0]

            elif igMatch:
                self.host = 'instagram'
                embedUrl = video_url

            elif twitterMatch:
                self.host = 'twitter'
                embedUrl = video_url

            elif twitchMatch:
                self.host = 'twitch'
                self.domain = self.env['ir.config_parameter'].sudo().get_param('customizations_by_livep.domain')
                #self.domain = 'localhost'
                print('My Domain', self.domain)

                embedUrl = "https://player.twitch.tv/?channel={}&parent={}".format(twitchMatch.groups()[0], self.domain)

            elif weiboMatch:
                self.host = 'weibo'
                embedUrl = video_url

            else:
                # We directly use the provided URL as it is
                embedUrl = video_url

            self.embed_url = embedUrl
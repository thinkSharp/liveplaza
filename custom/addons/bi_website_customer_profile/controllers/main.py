# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

from odoo import http, _
from odoo.exceptions import AccessError
from odoo.http import request
from odoo.addons.portal.controllers.portal import CustomerPortal
import base64
import json


class customerprofile(CustomerPortal):

    @http.route(['/my/profile'], type='http', auth="public", website=True)
    def partner_profile(self, page=1, **kwargs):
        values = {}
        param = request.env['ir.config_parameter'].sudo()
        param.set_param('auth_signup.reset_password', True)

        partner = request.env.user.partner_id
        shipping_address = request.env['res.partner'].search(
            [['parent_id', '=', partner.id], ['type', '=', 'delivery']])
        billing_address = request.env['res.partner'].search(
            [['parent_id', '=', partner.id], ['type', '=', 'invoice']])
        values.update({'sh_address': shipping_address,
                       'inv_address': billing_address})
        return request.render("bi_website_customer_profile.bi_portal_my_profile", values)

    @http.route(['/my/profile/edit', '/my/profile/edit/page/<int:page>'], type='http', auth="public", website=True)
    def partner_profile_edit(self, page=1, **kwargs):
        partner = request.env.user.partner_id
        partner_township = partner.township_id.id
        partner_state = partner.township_id.state_id.id 
                
        return request.render("bi_website_customer_profile.bi_portal_my_profile_edit", {'partner': partner, 'partner_township' : partner_township, 'partner_state': partner_state})

    @http.route(['/my/profile/thankyou'], type='http', auth="public", website=True)
    def edit_your_profile(self, **post):
        pic1 = post['picture']
        
        partner_obj = request.env['res.partner'].sudo().search(
            [('id', '=', post['id'])])
        
        township = request.env['res.country.township'].sudo().search(
            [('id', '=', post['township_id'])])
        
        if pic1:
            pic = base64.encodestring(pic1.read())
            for i in partner_obj:
                i.update({'name': post['name'],
                        'city': post['city'],
                        # disabled by KMS
                        # 'company_name': post['company_name'],
                        # 'function': post['function'],
                        # 'zip': post['zip'],
                        'street': post['street'],
                        'street2': post['street2'],
                        'phone': post['phone'],
                        'mobile': post['mobile'],
                        'email': post['email'],
                        'township_id': post['township_id'],
                        'state_id': township.state_id.id,
                        'country_id': int(post['country_id']),
                        'image_1920': pic,
                        })
        else:
            for i in partner_obj:
                i.update({'name': post['name'],
                        'city': post['city'],
                        # disabled by KMS
                        # 'company_name': post['company_name'],
                        # 'function': post['function'],
                        # 'zip': post['zip'],
                        'street': post['street'],
                        'street2': post['street2'],
                        'phone': post['phone'],
                        'mobile': post['mobile'],
                        'email': post['email'],
                        'township_id': post['township_id'],
                        'state_id': township.state_id.id,
                        'country_id': int(post['country_id']),
                        })

        return request.render("bi_website_customer_profile.profile_thankyou")

    @http.route(['/my/shipping_address/edit', '/my/shipping_address/edit/<int:sh_id>'], type='http', auth="public", website=True)
    def partner_shipping_address_edit(self, sh_id=False, **kwargs):
        partner = request.env['res.partner'].browse(sh_id)
        partner_township = partner.township_id.id
        partner_state = partner.township_id.state_id.id 
        if partner:
            return request.render("bi_website_customer_profile.bi_portal_my_shipping_edit", {'partner': partner, 'partner_township' : partner_township, 'partner_state': partner_state, 'option': 'edit'})
        else:
            return request.render("bi_website_customer_profile.bi_portal_my_shipping_edit", {'partner': request.env.user.partner_id, 'partner_township' : partner_township, 'partner_state': partner_state, 'option': 'create'})

    @http.route(['/shipping_address/delete/<int:sh_id>'], type='http', auth="public", website=True)
    def partner_shipping_address_delete(self, sh_id=False, **kwargs):
        partner = request.env['res.partner'].browse(sh_id)
        try:
            with http.request.env.cr.savepoint():
                partner.unlink()
                return request.redirect('/my/profile')
        except:
            return request.redirect('/error_page/shipping')

    @http.route(['/shipping_address/thankyou'], type='http', auth="public", website=True)
    def edit_your_shipping_address(self, **post):
        shipping_address = request.env['res.partner'].sudo().search(
            [('id', '=', post['id']), ('type', '=', 'delivery')], limit=1)
        
        township = request.env['res.country.township'].sudo().search(
            [('id', '=', post['township_id'])])

        if shipping_address:
            shipping_address.write({
                'name': post['name'],
                'city': post['city'],
                # disabled by KMS
                # 'zip': post['zip'],
                'street': post['street'],
                'street2': post['street2'],
                'phone': post['phone'],
                'mobile': post['mobile'],
                'email': post['email'],
                'township_id': post['township_id'],
                'state_id': township.state_id.id,
                'country_id': int(post['country_id']),
            })
        else:
            partner_obj = request.env['res.partner'].sudo().search(
                [('id', '=', post['id'])])
            shipping_address = partner_obj.child_ids.create({
                'type': 'delivery',
                'parent_id': partner_obj.id,
                'name': post['name'],
                'city': post['city'],
                # disabled by KMS
                # 'zip': post['zip'],
                'street': post['street'],
                'street2': post['street2'],
                'phone': post['phone'],
                'mobile': post['mobile'],
                'email': post['email'],
                'township_id': post['township_id'],
                'state_id': township.state_id.id,
                'country_id': int(post['country_id']),
            })
        return request.render("bi_website_customer_profile.shipping_address_thankyou")

    @http.route(['/my/billing_address/edit', '/my/billing_address/edit/<int:bl_id>'], type='http', auth="public", website=True)
    def partner_billing_address_edit(self, bl_id=False, **kwargs):
        partner = request.env['res.partner'].browse(bl_id)
        partner_township = partner.township_id.id
        partner_state = partner.township_id.state_id.id
        if partner:
            return request.render("bi_website_customer_profile.bi_portal_my_billing_edit", {'partner': partner, 'partner_township' : partner_township, 'partner_state': partner_state, 'option': 'edit'})
        else:
            return request.render("bi_website_customer_profile.bi_portal_my_billing_edit", {'partner': request.env.user.partner_id, 'partner_township' : partner_township, 'partner_state': partner_state, 'option': 'create'})

    @http.route(['/billing_address/delete/<int:bl_id>'], type='http', auth="public", website=True)
    def partner_billing_address_delete(self, bl_id=False, **kwargs):
        partner = request.env['res.partner'].browse(bl_id)
        try:
            with http.request.env.cr.savepoint():
                partner.unlink()
                return request.redirect('/my/profile')
        except:
            return request.redirect('/error_page/billing')

    @http.route(['/billing_address/thankyou'], type='http', auth="public", website=True)
    def edit_your_billing_address(self, **post):
        billing_address = request.env['res.partner'].sudo().search(
            [('id', '=', post['id']), ('type', '=', 'invoice')], limit=1)
        
        township = request.env['res.country.township'].sudo().search(
            [('id', '=', post['township_id'])])

        if billing_address:
            billing_address.write({
                'name': post['name'],
                'city': post['city'],
                # disabled by KMS
                # 'zip': post['zip'],
                'street': post['street'],
                'street2': post['street2'],
                'phone': post['phone'],
                'mobile': post['mobile'],
                'email': post['email'],
                'township_id': post['township_id'],
                'state_id': township.state_id.id,
                'country_id': int(post['country_id']),
            })
        else:
            partner_obj = request.env['res.partner'].sudo().search(
                [('id', '=', post['id'])])
            billing_address = partner_obj.child_ids.create({
                'type': 'invoice',
                'parent_id': partner_obj.id,
                'name': post['name'],
                'city': post['city'],
                # disabled by KMS
                # 'zip': post['zip'],
                'street': post['street'],
                'street2': post['street2'],
                'phone': post['phone'],
                'mobile': post['mobile'],
                'email': post['email'],
                'township_id': post['township_id'],
                'state_id': township.state_id.id,
                'country_id': int(post['country_id']),
            })
        return request.render("bi_website_customer_profile.billing_address_thankyou")

    @http.route(['/error_page/shipping'], type='http', auth="public", website=True)
    def error_shipping_address(self, **post):
        return request.render("bi_website_customer_profile.error_page", {'address': 'shipping'})

    @http.route(['/error_page/billing'], type='http', auth="public", website=True)
    def error_billing_address(self, **post):
        return request.render("bi_website_customer_profile.error_page", {'address': 'billing'})

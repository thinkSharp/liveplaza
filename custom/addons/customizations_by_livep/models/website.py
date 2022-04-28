# -*- coding: utf-8 -*- --

from odoo import api, fields, models, _


class Website(models.Model):
    _inherit = 'website'

    def get_subscription_plans(self):
        sub_plans = self.env['subscription.plan'].sudo().search([('id','=',8)])
        return  sub_plans

    def get_townships(self):
        townships = self.env['res.country.township'].sudo().search([])
        return  townships


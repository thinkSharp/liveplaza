# -*- coding: utf-8 -*- --

from odoo import api, fields, models, _
from odoo.http import request

class Website(models.Model):
    _inherit = 'website'

    def get_subscription_plans(self):
        sub_plans = self.env['subscription.plan'].sudo().search([('id','=',8)])
        return  sub_plans

    def get_townships(self):
        townships = self.env['res.country.township'].sudo().search([])
        return  townships

    def get_checked_sale_order_line(self, order):
        # sale_order = self.env['sale.order'].with_context().sudo().browse(sale_order_id).exists() if sale_order_id else None
        checked_list = []
        if isinstance(order, list):
            for line in order:
                line_tmp = self.env['sale.order.line'].sudo().browse(int(line))
                print(line_tmp)
                if line_tmp.selected_checkout == True:
                    checked_list.append(line_tmp.id)


        else:
            for line in order:
                if line.selected_checkout == True:
                    checked_list.append(line)

        return checked_list

    def get_sale_order_id_list(self):
        order = self.sale_get_order()
        idList = []

        for o in order.website_order_line:
            idList.append(o.id)

        return idList

    def sale_replace(self, sale_order_id, website_sale_current_pl):
        request.session.update({
            'sale_order_id': sale_order_id,
            'website_sale_current_pl': website_sale_current_pl,
        })
        
    def newlp_so_website(self, order):
        request.session.update({
            'newlp_sale_order_id': order.id,
            'newlp_website_sale_current_pl': order.pricelist_id.id,
        })

    # def get_checked_sale_order_line(self):
    #     order = self.sale_get_order()
    #     checked_list = []
    #
    #     for o in order.website_order_line:
    #         if o.selected_checkout == True:
    #             checked_list.append(o)
    #
    #     return checked_list
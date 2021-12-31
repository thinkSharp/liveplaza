# -*- coding: utf-8 -*-

from odoo import fields, models, api, _


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    def action_confirm(self):
        res = super(SaleOrder, self).action_confirm()
        
        ### For auto assigning delivery vendor ###
        # buyer_township = self.partner_shipping_id.township_id        
        # all_deli_zone = self.env['delivery.method'].search([])
        # delivery_zone = 0
        # delivery_vendor = 0
        # for deli_zone in all_deli_zone:
        #     if buyer_township in deli_zone.township_ids:
        #         delivery_zone = int(deli_zone.id)
        #         delivery_vendor = int(deli_zone.related_partner_id.id)
        # deli_vals = {
        #     'vendor_id': delivery_vendor,
        #     'delivery_method_id': delivery_zone,
        # }
        # for do_pick in self.picking_ids:
        #     do_pick.write(deli_vals)
        ### END ###

        return res


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    picking_move_count = fields.Integer(compute='compute_count')
    packaging_move_count = fields.Integer(compute='compute_count')
    is_picked = fields.Boolean('Picked', default=False)
    is_packaged = fields.Boolean('Packaged', default=False)   
    is_paid = fields.Boolean('Paid', default=False)
    is_ready = fields.Boolean('Ready to Pick', default=False)
    marketplace_status = fields.Boolean("MarketPlace State", default=False)
    
    def button_approve(self):
        for rec in self:              
            rec.sudo().marketplace_state = "approved"
            rec.sudo().marketplace_status = True
   
    def button_approve_ol(self):
        for rec in self:
            order = self.env['sale.order'].search([('id','=',rec.order_id.id)])
            if order.get_portal_last_transaction().acquirer_id.name == 'Cash on Delivery':
                if rec.product_id.type == 'service':
                    rec.sudo().marketplace_state = "shipped"
                else:
                    rec.sudo().marketplace_state = "approved"
                    rec.sudo().marketplace_status = True
            else:    
                if rec.product_id.type == 'service':
                    rec.sudo().marketplace_state = "shipped"
                else:
                    rec.sudo().marketplace_state = "new"
    
    def action_ready(self):
        self.ensure_one()
        self.is_ready = True
        domain = [('mp_order_id', '=', self.id)]
        picked_record = self.env['picking.move'].search(domain)
        if picked_record:
            picked_record.sudo().write({
                'is_ready': True,
            })
        inv_domain = [('id', '=', self.order_id.invoice_ids.id)]
        invoice_record = self.env['account.move'].search(inv_domain)
        if invoice_record:
            invoice_record.sudo().action_post()
    
    def action_get_picking(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Picked',
            'view_mode': 'tree',
            'res_model': 'picking.move',
            'domain': [('mp_order_id', '=', self.id)],
            'context': "{'create': False}"
        }
        
    def action_get_packaging(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Packed',
            'view_mode': 'tree',
            'res_model': 'packaging.move',
            'domain': [('mp_order_id', '=', self.id)],
            'context': "{'create': False}"
        }

    def compute_count(self):
        for record in self:
            record.picking_move_count = self.env['picking.move'].search_count(
                [('mp_order_id', '=', self.id)])
            record.packaging_move_count = self.env['packaging.move'].search_count(
                [('mp_order_id', '=', self.id)])
    
    def generate_pickup_move(self):
        picking_address = self.marketplace_seller_id.id
        seller_township = self.marketplace_seller_id.township_id
        all_zone = self.env['picking.method'].search([])
        pickup_zone = 0
        vendor = 0
        for zone in all_zone:
            if seller_township in zone.township_ids:
                pickup_zone = int(zone.id)
                # vendor = int(zone.related_partner_id.id)
        date = self.create_date
        origin = self.order_id.name

        pickup_vals = {
            'name': 'New',
            'scheduled_date': date,
            'origin': origin,
            'mp_order_id': self.id,
            'picking_address': picking_address,
            'vendor_id': vendor,
            'picking_method_id': pickup_zone,
            'state': 'draft',
        }

        return self.env['picking.move'].create(pickup_vals)


    def generate_packaging_move(self):
        seller_id = 0
        date = self.create_date
        origin = self.order_id.name
        seller_id = self.marketplace_seller_id.id
        

        packaging_vals = {
            'name': 'New',
            'scheduled_date': date,
            'origin': origin,
            'mp_order_id': self.id,
            'marketplace_seller_id': seller_id,
            'state': 'draft',
        }

        return self.env['packaging.move'].create(packaging_vals)

# -*- coding: utf-8 -*-

from odoo import fields, models, api, _
from odoo.exceptions import UserError, ValidationError
import json

class DeliveryMethod(models.Model):
    _name = 'delivery.method'
    _description = 'Delivery Zone'

    name = fields.Char(string='Name', store=True, required=True,
                       copy=False, index=True)
    deli_price = fields.Float(
        string='Price', store=True, copy=False, index=False)
    active = fields.Boolean('Active', default=True)
    related_partner_ids = fields.Many2many(
        'res.partner', 'partner_deli_rel', string='Vendor', readonly=True)
    township_ids = fields.Many2many(
        'res.country.township', 'deli_tshp_rel', string='Allowed Townships')
    last_used_sequence = fields.Float(string="Last Used Sequence", default=0)
    delivery_vendor_company = fields.Many2one('res.partner', required=True, string='Delivery Vendor Company')
    delivery_vendor_domain = fields.Char(compute="_compute_delivery_vendor_domain", readonly=True, store=False)

    @api.depends('name')
    def _compute_delivery_vendor_domain(self):
        for rec in self:
            user_obj = self.env['res.users'].sudo().browse(rec._uid)
            united_list = []
            if user_obj.partner_id and user_obj.partner_id.is_default:
                if not user_obj.has_group('base.group_system'):
                    for b_id in user_obj.partner_id:
                        united_list.append(b_id.id)
                else:
                    all_vendor_ids = self.env['res.partner'].search([('is_default', '=', True),('delivery_vendor', '=', True),
                                                                   ('picking_vendor', '=', True), ('active', '=', True)])
                    if all_vendor_ids:
                        for v_id in all_vendor_ids:
                            united_list.append(v_id.id)
            else:
                all_vendor_ids = self.env['res.partner'].search(
                    [('is_default', '=', True), ('delivery_vendor', '=', True),
                     ('picking_vendor', '=', True), ('active', '=', True)])
                if all_vendor_ids:
                    for v_id in all_vendor_ids:
                        united_list.append(v_id.id)
            rec.delivery_vendor_domain = json.dumps([('id', 'in', united_list)])

    @api.model
    def create(self, vals):
        township_obj = self.env['res.country.township']
        if vals.get("township_ids", False):
            township_obj = self.env['res.country.township'].search([('id', 'in', vals.get("township_ids")[0][2])])
        if vals.get("delivery_vendor_company", False):
            partner_obj = self.env['delivery.method'].search([('delivery_vendor_company', '=', vals.get("delivery_vendor_company"))])
            if partner_obj and township_obj:
                for town_data in township_obj:
                    if town_data in partner_obj.township_ids:
                        raise UserError(_(" %s Township is already configured in %s Zone. Please select another township for this Zone.") % (town_data.name, partner_obj.name))
        return super(DeliveryMethod, self).create(vals)

    def write(self, vals):
        township_obj = self.env['res.country.township']
        if vals.get("township_ids", False):
            township_obj = self.env['res.country.township'].search([('id', 'in', vals.get("township_ids")[0][2])])
        if self.delivery_vendor_company:
            partner_obj = self.env['delivery.method'].search([('delivery_vendor_company', '=', self.delivery_vendor_company.id),('id', '!=', self.id)])
            if partner_obj and township_obj:
                for town_data in township_obj:
                    for picking_M in partner_obj:
                        if town_data in picking_M.township_ids:
                            raise UserError(_(" %s Township is already configured in %s Zone. Please select another township for this Zone.") % (town_data.name, picking_M.name))
        return super(DeliveryMethod, self).write(vals)
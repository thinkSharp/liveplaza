# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from ast import literal_eval
from datetime import date
from datetime import datetime, timedelta
from itertools import groupby
from operator import itemgetter
import time

from odoo import api, fields, models, SUPERUSER_ID, _
from odoo.osv import expression
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
from odoo.tools.float_utils import float_compare, float_is_zero, float_round
from odoo.exceptions import UserError
from odoo.addons.stock.models.stock_move import PROCUREMENT_PRIORITIES
import datetime


class Picking(models.Model):
    _inherit = "stock.picking"

    payment_provider = fields.Selection(selection=[('manual', 'Custom Payment Form'),('transfer', 'Prepaid'),
                                                    ('cash_on_delivery', 'COD'),('wavepay', 'WavePay')], string='Payment Type')
    
    is_admin_approved = fields.Boolean('Admin Approved', default=False) 
    
    ready_to_pick = fields.Boolean('Ready to Pick', default=False)
    
    township_id = fields.Many2one('res.country.township', related="marketplace_seller_id.township_id",  string="Township", readonly=False, store=True)
    
    state_id = fields.Many2one('res.country.state', related="marketplace_seller_id.state_id", string="State", readonly=False, store=True)
    
    street = fields.Char(related="marketplace_seller_id.street", string="Street", readonly=False, store=True)
    
    buyer_township_id = fields.Many2one('res.country.township', related="partner_id.township_id", string="Township", readonly=False, store=True)
    
    buyer_state_id = fields.Many2one('res.country.state', related="partner_id.state_id", string="State", readonly=False, store=True)
    
    buyer_street = fields.Char(related="partner_id.street", string="Street", readonly=False, store=True)    
    
    buyer_street2 = fields.Char(related="partner_id.street2", string="Street", readonly=False, store=True)
    
    picking_method_id = fields.Many2one('picking.method', string='Pickup Zone', ondelete='cascade')
    
    delivery_person_id = fields.Many2one('res.partner', states={'draft': [('readonly', False)]},
            domain="['|', ('company_type', '=', 'individual'), ('delivery_vendor', '=', True)]", string='Delivery Person') 
    
    pickup_person_id = fields.Many2one('res.partner', states={'draft': [('readonly', False)]},
            domain="['|', ('company_type', '=', 'individual'), ('picking_vendor', '=', True)]", string='Pickup Person') 
    
    state = fields.Selection([
            ('draft', 'Draft'),
            ('waiting', 'Waiting Another Operation'),
            ('confirmed', 'Waiting'),
            ('assigned', 'Ready'),
            ('delivering', 'Delivering Now'),
            ('done', 'Done'),
            ('cancel', 'Cancelled'),
            ('hold', 'Hold'),
        ], string='Status', compute='_compute_state',
            copy=False, index=True, readonly=True, store=True, tracking=True)
    
    old_state = fields.Char(string="Old Status", readonly=True, store=True)
    
    pick_date = fields.Datetime('Pick Date', store=True)
    pack_date = fields.Datetime('Pack Date', store=True)
    delivery_date = fields.Datetime('Delivery Date', store=True)

    def deliver_now(self):
        picking = self.env["stock.picking"].search(
            [('origin', '=', self.origin), ('picking_type_id.name', '=', self.picking_type_id.name)])
        order = self.env["sale.order"].search([('name', '=', self.origin)])
        if self.state == 'assigned':
            self.write({'state': 'delivering'})
            if self.check_all_order_deliver(picking):
                order.delivery_status = 'delivering'
                order.delivering_date = datetime.datetime.now()

    def check_all_order_deliver(self, picking):
        for p in picking:
            if p.state != "delivering":
                return False
        return True

    
    def do_hold(self):
        if self.state == 'hold':
            self.write({'state': self.old_state, 'old_state': ''})            
        else:
            self.write({'state': 'hold', 'old_state': self.state, 'hold_date': datetime.now()})    
    
    def action_done(self):
        """Changes picking state to done by processing the Stock Moves of the Picking

        Normally that happens when the button "Done" is pressed on a Picking view.
        @return: True
        """

        self.ensure_one()

        self._check_company()
        seller_payment = self.env['seller.payment']
        account_payment = self.env['account.payment']
        
        todo_moves = self.mapped('move_lines').filtered(lambda self: self.state in ['draft', 'waiting', 'partially_available', 'assigned', 'confirmed'])
        # Check if there are ops not linked to moves yet
        for pick in self:
            if pick.owner_id:
                pick.move_lines.write({'restrict_partner_id': pick.owner_id.id})
                pick.move_line_ids.write({'owner_id': pick.owner_id.id})

            # # Explode manually added packages
            # for ops in pick.move_line_ids.filtered(lambda x: not x.move_id and not x.product_id):
            #     for quant in ops.package_id.quant_ids: #Or use get_content for multiple levels
            #         self.move_line_ids.create({'product_id': quant.product_id.id,
            #                                    'package_id': quant.package_id.id,
            #                                    'result_package_id': ops.result_package_id,
            #                                    'lot_id': quant.lot_id.id,
            #                                    'owner_id': quant.owner_id.id,
            #                                    'product_uom_id': quant.product_id.uom_id.id,
            #                                    'product_qty': quant.qty,
            #                                    'qty_done': quant.qty,
            #                                    'location_id': quant.location_id.id, # Could be ops too
            #                                    'location_dest_id': ops.location_dest_id.id,
            #                                    'picking_id': pick.id
            #                                    }) # Might change first element
            # # Link existing moves or add moves when no one is related
            for ops in pick.move_line_ids.filtered(lambda x: not x.move_id):
                # Search move with this product
                moves = pick.move_lines.filtered(lambda x: x.product_id == ops.product_id)
                moves = sorted(moves, key=lambda m: m.quantity_done < m.product_qty, reverse=True)
                if moves:
                    ops.move_id = moves[0].id
                else:
                    new_move = self.env['stock.move'].create({
                                                    'name': _('New Move:') + ops.product_id.display_name,
                                                    'product_id': ops.product_id.id,
                                                    'product_uom_qty': ops.qty_done,
                                                    'product_uom': ops.product_uom_id.id,
                                                    'description_picking': ops.description_picking,
                                                    'location_id': pick.location_id.id,
                                                    'location_dest_id': pick.location_dest_id.id,
                                                    'picking_id': pick.id,
                                                    'picking_type_id': pick.picking_type_id.id,
                                                    'restrict_partner_id': pick.owner_id.id,
                                                    'company_id': pick.company_id.id,
                                                   })
                    ops.move_id = new_move.id
                    new_move._action_confirm()
                    todo_moves |= new_move
                    #'qty_done': ops.qty_done})
        todo_moves._action_done(cancel_backorder=self.env.context.get('cancel_backorder'))
        self.write({'date_done': fields.Datetime.now()})
        
        if self.picking_type_id.name == 'Pick':
            self.write({'pick_date': fields.Datetime.now()})
        elif self.picking_type_id.name == 'Pack':
            self.write({'pack_date': fields.Datetime.now()})
        elif self.picking_type_id.name == 'Delivery Orders':
            self.write({'delivery_date': fields.Datetime.now()})
            sp_obj = seller_payment.create(self.prepare_seller_payment_vals())
            if sp_obj:
                sp_obj.do_validate()
                sp_obj.do_Confirm_and_view_invoice()
                sp_obj.invoice_id.sudo().action_post()
                #account_payment_dict = sp_obj.invoice_id.sudo().action_invoice_register_payment()

                if sp_obj.invoice_id.is_inbound():
                    domain = [('payment_type', '=', 'inbound')]
                else:
                    domain = [('payment_type', '=', 'outbound')]
                
                invoices = self.env['account.move'].browse(sp_obj.invoice_id.id).filtered(lambda move: move.is_invoice(include_receipts=True))
                
                values = {
                        'journal_id': self.journal_id.id,                        
                        'payment_date': sp_obj.date,
                        'payment_method_id': self.env['account.payment.method'].search(domain, limit=1).id,
                        'communication': sp_obj.invoice_id.name,
                        'invoice_ids': [(6, 0, invoices.ids)],
                        'payment_type': 'outbound',
                        'partner_type': 'seller',
                        'amount': abs(sp_obj.invoice_id.amount_total),
                        'currency_id': sp_obj.invoice_id.currency_id.id,
                        'partner_id': sp_obj.invoice_id.commercial_partner_id.id,
                    }
                #acc_payment_id = account_payment.create(values)                
                #acc_payment_id.sudo().post()
                
                sp_obj.invoice_id.sudo().post()
                sp_obj.do_paid()

        picking = self.env["stock.picking"].search(
            [('origin', '=', self.origin), ('picking_type_id.name', '=', self.picking_type_id.name)])
        order = self.env["sale.order"].search([('name', '=', self.origin)])
        picking_type = self.picking_type_id.name

        if self.check_all_order_done(picking):
            if picking_type == "Pick":
                order.delivery_status = 'picked'
                order.picking_date = datetime.datetime.now()
            elif picking_type == "Pack":
                order.delivery_status = 'packed'
                order.packing_date = datetime.datetime.now()
            elif picking_type == "Delivery Orders":
                if self.state == 'delivering':
                    order.delivery_status = "delivering"
                    order.delivering_date = datetime.datetime.now()
                elif self.state == 'done':
                    order.delivery_status = "delivered"
                    order.delivered_date = datetime.datetime.now()
            else:
                order.delivery_status = "ordered"

        self._send_confirmation_email()
        return True

    def check_all_order_done(self, picking):
        for p in picking:
            if p.state != "done":
                return False
        return True

    def button_validate(self):
        self.ensure_one()

        if not self.move_lines and not self.move_line_ids:
            raise UserError(_('Please add some items to move.'))


        # Clean-up the context key at validation to avoid forcing the creation of immediate
        # transfers.
        ctx = dict(self.env.context)
        ctx.pop('default_immediate_transfer', None)
        self = self.with_context(ctx)

        # add user as a follower
        self.message_subscribe([self.env.user.partner_id.id])

        # If no lots when needed, raise error
        picking_type = self.picking_type_id
        precision_digits = self.env['decimal.precision'].precision_get('Product Unit of Measure')
        no_quantities_done = all(float_is_zero(move_line.qty_done, precision_digits=precision_digits) for move_line in self.move_line_ids.filtered(lambda m: m.state not in ('done', 'cancel')))
        no_reserved_quantities = all(float_is_zero(move_line.product_qty, precision_rounding=move_line.product_uom_id.rounding) for move_line in self.move_line_ids)
        if no_reserved_quantities and no_quantities_done:
            raise UserError(_('You cannot validate a transfer if no quantites are reserved nor done. To force the transfer, switch in edit more and encode the done quantities.'))

        if picking_type.use_create_lots or picking_type.use_existing_lots:
            lines_to_check = self.move_line_ids
            if not no_quantities_done:
                lines_to_check = lines_to_check.filtered(
                    lambda line: float_compare(line.qty_done, 0,
                                               precision_rounding=line.product_uom_id.rounding)
                )

            for line in lines_to_check:
                product = line.product_id
                if product and product.tracking != 'none':
                    if not line.lot_name and not line.lot_id:
                        raise UserError(_('You need to supply a Lot/Serial number for product %s.') % product.display_name)

        # Propose to use the sms mechanism the first time a delivery
        # picking is validated. Whatever the user's decision (use it or not),
        # the method button_validate is called again (except if it's cancel),
        # so the checks are made twice in that case, but the flow is not broken
        sms_confirmation = self._check_sms_confirmation_popup()
        if sms_confirmation:
            return sms_confirmation

        print("before no_quantities_done")
        if no_quantities_done:
            view = self.env.ref('stock.view_immediate_transfer')
            wiz = self.env['stock.immediate.transfer'].create({'pick_ids': [(4, self.id)]})
            return {
                'name': _('Immediate Transfer?'),
                'type': 'ir.actions.act_window',
                'view_mode': 'form',
                'res_model': 'stock.immediate.transfer',
                'views': [(view.id, 'form')],
                'view_id': view.id,
                'target': 'new',
                'res_id': wiz.id,
                'context': self.env.context,
            }

        print("after no_quantities_done")

        if self._get_overprocessed_stock_moves() and not self._context.get('skip_overprocessed_check'):
            view = self.env.ref('stock.view_overprocessed_transfer')
            wiz = self.env['stock.overprocessed.transfer'].create({'picking_id': self.id})
            return {
                'type': 'ir.actions.act_window',
                'view_mode': 'form',
                'res_model': 'stock.overprocessed.transfer',
                'views': [(view.id, 'form')],
                'view_id': view.id,
                'target': 'new',
                'res_id': wiz.id,
                'context': self.env.context,
            }

        # Check backorder should check for other barcodes
        if self._check_backorder():
            return self.action_generate_backorder_wizard()
        self.action_done()
        return


    
    def prepare_seller_payment_vals(self):        
    
        payable_to_seller = 0
        so_line_id = self.env['sale.order.line'].search([('order_id', '=', self.env['sale.order'].search([('name', '=', self.origin)]).id )])  
        
        for sol_data in so_line_id:
            if self.marketplace_seller_id.id == sol_data.marketplace_seller_id.id:
                payable_to_seller += (sol_data.price_subtotal - sol_data.commission_amount)
            
        return {'state': 'draft',
                'name': 'NEW',
                'date': self.scheduled_date,
                'payment_type': 'cr',
                'seller_id': self.marketplace_seller_id.id,
                'payment_mode': 'order_paid',
                'memo': self.origin or '',
                'payable_amount': payable_to_seller,
                'payment_method': False,
                'description': 'Payable amount to seller' + self.marketplace_seller_id.name or '',
                'message_attachment_count': 0,
            }
        
    def compute_receivable_delivery(self):

        lines = self.mapped('sale_id.order_line').filtered(lambda lines: lines.marketplace_seller_id.id == self.marketplace_seller_id.id)
        delivery_amount = 0.0
        receivable_amount = 0.0
        if lines:
            payments = self.env['account.move'].search([('ref', '=', self.sale_id.name)])            
            delivery_domain = [('order_id', '=', self.sale_id.id), ('is_delivery', '=', True)]
            delivery_line = self.env['sale.order.line'].search(delivery_domain)            
            
            if delivery_line:
                delivery_amount = delivery_line.price_subtotal                        
            
            for line in lines:
                for pick_data in self.move_line_ids_without_package:
                    if pick_data.product_id == line.product_id:
                        receivable_amount += line.price_subtotal
                
            if not payments:
                self.write({
                    'receivable_amount_stored': receivable_amount,
                    'delivery_amount_stored': delivery_amount,
                })
            else:
                self.write({
                    'receivable_amount_stored': receivable_amount,
                    'delivery_amount_stored':  delivery_amount,
                })
    
    @api.onchange('scheduled_date')
    def _onchange_scheduled_date(self):
        next_date = datetime.now() + timedelta(days=21)
        previous_date = datetime.now() - timedelta(days=21)
        if datetime.now() <= next_date or datetime.now() >= previous_date:            
            raise UserError('Your delivery time is more than 21 days ahead. Please check.')
    
    
    
    
    
import datetime

from odoo import fields, models, api, _, exceptions
import string
import random


class Ticket(models.Model):
    _name = 'booking.ticket'
    _description = 'Booking Ticket Code'

    name = fields.Char(string='Request', required=True, copy=False, index=True, readonly=True, default=lambda self: self.product)

    ticket_code = fields.Char(string='Code', required=True, copy=False, index=True, readonly=True)
    state = fields.Selection([
        ('active', 'Active'),
        ('used', 'Used'),
        ('expired', 'Expired'),
    ], string='Status', readonly=True, copy=False, index=True, default='active')

    seller = fields.Many2one("res.partner", string="Seller", readonly=True)
    customer = fields.Many2one("res.partner", string="Buyer", readonly=True)
    sale_order = fields.Many2one("sale.order", string="Sale Order", readonly=True)
    product = fields.Many2one("product.product", string="Product", readonly=True)

    resent_times = fields.Integer(default = 0)
    mobile = fields.Char()

    booking_date = fields.Date()
    booked_slot =  fields.Char()
    booked_plan =  fields.Char()

    def action_validate(self):
        super(Ticket, self).write({'state': 'used'})


    def action_reset(self):
        super(Ticket, self).write({'state': 'active'})

    def action_resend(self):
        sms_template_objs = self.env["wk.sms.template"].sudo().search(
            [('condition', '=', 'booking_ticket_ready'), ('globally_access', '=', False)])
        for sms_template_obj in sms_template_objs:
            mobile = sms_template_obj._get_partner_mobile(self.customer)
            if mobile:
                sms_template_obj.send_sms_using_template(
                    mobile, sms_template_obj, obj=self)

        self.write({'resent_times': self.resent_times+1})


    @api.depends('partner_id')
    def _get_partner(self):
        partner = self.env['res.users'].browse(self.env.uid).partner_id
        for rec in self:
            rec.partner_id = partner.id

    @api.model
    def create(self, vals):
        vals['name'] = vals["temp_product"].name
        del vals["temp_product"]
        result = super(Ticket, self).create(vals)
        return result


class TicketSearchWizard(models.TransientModel):
    _name = 'booking.ticket.wizard'

    ticket_code = fields.Char(string='Booking Ticket Code: ', required=True)
    mobile = fields.Char(string='Mobile No: ', required=True)
    seller = fields.Many2one("res.partner", string="Seller", default=lambda self: self.env.user.partner_id.id if self.env.user.partner_id and self.env.user.partner_id.seller else self.env['res.partner'])

    def search_ticket(self):
        print('Mobile', self.mobile)
        print('Ticket Code', self.ticket_code)
        ticket = self.env['booking.ticket'].search([('ticket_code', '=', self.ticket_code), ('mobile', '=', self.mobile), ('seller', '=', self.seller.id)])
        print('Mobile', self.mobile)
        print('Ticket Code', self.ticket_code)


        if ticket:
            return {
                "res_model": "booking.ticket",
                'res_id': ticket.id,
                "type": "ir.actions.act_window",
                "view_mode":  "form",
                "view_type": "form",
                "view_id": self.env.ref("website_booking_system.booking_ticket_search_form_view").id,
                "target": "self"
            }

        else:
            raise exceptions.ValidationError(_('Invalid ticket_code or mobile_no or seller.'))



class SaleOrder(models.Model):
    _inherit = "sale.order"

    def booking_ticket_process(self):
        random_elements = list(string.ascii_letters + string.digits)

        sale_order_lines = self.env['sale.order.line'].sudo().search(
            [('order_id', '=', self.id)])

        print("Sale order line", sale_order_lines)



        for line in sale_order_lines:
            print('Product Id', line.product_id)

            if line.product_id.is_booking_type:
                for i in range(int(line.product_qty)):
                    while True:
                        # generate ticket code and check if there is already exists in database.
                        # if it already exists, regenerate code.

                        ticket_code_list = []
                        for i in range(10):
                            ticket_code_list.append(random.choice(random_elements))

                        ticket_code_list.insert(5,'-')

                        ticket_code = ''.join(ticket_code_list)

                        db_ticket_code = self.env['booking.ticket'].sudo().search([('ticket_code', '=', ticket_code)])
                        if not db_ticket_code:
                            break





                    mobile = self.partner_id.mobile if self.partner_id.mobile else self.partner_id.phone
                    vals = {
                        'ticket_code': ticket_code,
                        'seller': line.marketplace_seller_id.id,
                        'customer': self.partner_id.id,
                        'sale_order': self.id,
                        'product': line.product_id.id,
                        "temp_product": line.product_id,
                        'mobile': mobile,
                        'booking_date': line.booking_date,
                        'booked_slot': line.booked_slot_id.display_name,
                        'booked_plan': line.booked_plan_id.display_name
                    }

                    print(vals)

                    ticket_obj = self.env['booking.ticket'].sudo().create(vals)

                    mobile = self.partner_id.mobile if self.partner_id.mobile else self.partner_id.phone
                    if mobile:
                        # send sms
                        sms_template_objs = self.env["wk.sms.template"].sudo().search(
                            [('condition', '=', 'booking_ticket_ready'), ('globally_access', '=', False)])
                        for sms_template_obj in sms_template_objs:
                            mobile = sms_template_obj._get_partner_mobile(self.partner_id)
                            if mobile:
                                sms_template_obj.send_sms_using_template(
                                    mobile, sms_template_obj, obj=ticket_obj)

        return True




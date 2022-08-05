import datetime

from odoo import fields, models, api, _, exceptions
import string
import random


class Ticket(models.Model):
    _name = 'ticket'
    _description = 'Service Code'

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
    expiration_date = fields.Date()

    resent_times = fields.Integer(default = 0)
    mobile = fields.Char()



    def action_validate(self):
        if self.expiration_date:
            if self.expiration_date < datetime.date.today():
                super(Ticket, self).write({'state': 'expired'})

            else:
                super(Ticket, self).write({'state': 'used'})

        else:
            super(Ticket, self).write({'state': 'used'})


    def action_reset(self):
        super(Ticket, self).write({'state': 'active'})

    def action_resend(self):
        sms_template_objs = self.env["wk.sms.template"].sudo().search(
            [('condition', '=', 'ticket_ready'), ('globally_access', '=', False)])
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
    _name = 'ticket.wizard'

    ticket_code = fields.Char(string='Service Code: ', required=True)
    mobile = fields.Char(string='Mobile No: ', required=True)
    seller = fields.Many2one("res.partner", string="Seller", default=lambda self: self.env.user.partner_id.id if self.env.user.partner_id and self.env.user.partner_id.seller else self.env['res.partner'])

    def search_ticket(self):
        print('Mobile', self.mobile)
        print('Ticket Code', self.ticket_code)
        ticket = self.env['ticket'].search([('ticket_code', '=', self.ticket_code), ('mobile', '=', self.mobile), ('seller', '=', self.seller.id)])
        print('Mobile', self.mobile)
        print('Ticket Code', self.ticket_code)


        if ticket:
            return {
                "res_model": "ticket",
                'res_id': ticket.id,
                "type": "ir.actions.act_window",
                "view_mode":  "form",
                "view_type": "form",
                "view_id": self.env.ref("service_product.ticket_search_form_view").id,
                "target": "self"
            }

        else:
            raise exceptions.ValidationError(_('Invalid ticket_code or mobile_no.'))



class SaleOrder(models.Model):
    _inherit = "sale.order"
    contain_service = fields.Boolean("Service Ticket", compute="_compute_contain_service")
    all_service_ticket = fields.Boolean("All Service Ticket", compute="_compute_all_service_ticket")




    def ticket_process(self):
        random_elements = list(string.ascii_letters + string.digits)

        sale_order_lines = self.env['sale.order.line'].sudo().search(
            [('order_id', '=', self.id)])

        print("Sale order line", sale_order_lines)


        is_all_service = True
        for line in sale_order_lines:
            print('Product Id', line.product_id)

            if line.product_id.is_service:
                for i in range(int(line.product_qty)):
                    while True:
                        # generate ticket code and check if there is already exists in database.
                        # if it already exists, regenerate code.

                        ticket_code_list = []
                        for i in range(10):
                            ticket_code_list.append(random.choice(random_elements))

                        ticket_code_list.insert(5,'-')

                        ticket_code = ''.join(ticket_code_list)

                        db_ticket_code = self.env['ticket'].sudo().search([('ticket_code', '=', ticket_code)])
                        if not db_ticket_code:
                            break

                    days = int(line.product_id.expiration_policy)
                    if days:
                        expiration_date = datetime.date.today() + datetime.timedelta(days=days)
                    else:
                        expiration_date = None

                    mobile = self.partner_id.mobile if self.partner_id.mobile else self.partner_id.phone
                    vals = {
                        'ticket_code': ticket_code,
                        'seller': line.marketplace_seller_id.id,
                        'customer': self.partner_id.id,
                        'sale_order': self.id,
                        'product': line.product_id.id,
                        "temp_product": line.product_id,
                        'expiration_date': expiration_date,
                        'mobile': mobile
                    }

                    print(vals)

                    ticket_obj = self.env['ticket'].sudo().create(vals)


                    mobile = self.partner_id.mobile if self.partner_id.mobile else self.partner_id.phone
                    if mobile:
                        # send sms
                        sms_template_objs = self.env["wk.sms.template"].sudo().search(
                            [('condition', '=', 'ticket_ready'), ('globally_access', '=', False)])
                        for sms_template_obj in sms_template_objs:
                            mobile = sms_template_obj._get_partner_mobile(self.partner_id)
                            if mobile:
                                sms_template_obj.send_sms_using_template(
                                    mobile, sms_template_obj, obj=ticket_obj)
                    else:
                        # send email to users with their signup url
                        template = False


                        if not template:
                            template = self.env.ref('service_product.service_code_to_customer')
                        assert template._name == 'mail.template'
                        print("My Template", template)
                        template_values = {
                            'email_to': '${object.customer.email|safe}',
                            'email_cc': False,
                            'auto_delete': True,
                            'partner_to': False,
                            'scheduled_date': False,
                        }
                        template.write(template_values)

                        for ticket in ticket_obj:
                            if not ticket.customer.email:
                                raise UserError(_("Cannot send email: user %s has no email address.") % ticket.customer.name)
                            with self.env.cr.savepoint():
                                force_send = not (self.env.context.get('import_file', False))
                                print("TicketID", ticket, ticket.id)
                                template.with_context(lang=ticket.customer.lang).send_mail(ticket.id, force_send=force_send,
                                                                                raise_exception=True)
                            _logger.info("Password reset email sent for user")




            if (not line.product_id.is_service) and line.product_id.type == 'product':
                is_all_service = False
        return is_all_service

    @api.depends('order_line')
    def _compute_contain_service(self):
        for so in self:
            so.contain_service = any((line.selected_checkout and line.product_id.is_service == True) for line in so.order_line)

    @api.depends('order_line')
    def _compute_all_service_ticket(self):
        for so in self:
            for line in so.order_line:
                if line.selected_checkout and (not line.product_id.is_service):
                    so.all_service_ticket = False
                    break
                    # so.all_service_ticket = all(line.product_id.is_service == True for line in so.order_line)
            else:
                so.all_service_ticket = True
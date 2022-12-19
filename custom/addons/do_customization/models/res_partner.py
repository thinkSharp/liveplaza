
# -*- coding: utf-8 -*-

from odoo import SUPERUSER_ID, models, fields, api, _
from datetime import datetime, timedelta
from odoo.exceptions import MissingError
from lxml import etree
# from odoo.osv.orm import setup_modifiers
import decimal,re
from odoo.exceptions import except_orm, Warning, RedirectWarning, UserError
import logging
_logger = logging.getLogger(__name__)

manager_fields = []

class ResPartner(models.Model):
    _inherit = 'res.partner'

    is_default = fields.Boolean('Vendor Company', default=False)
    delivery_person = fields.Boolean(string="Is a Delivery Person", help="Check this box if the contact is delivery person.", copy=False, track_visibility='onchange')

class ResCompany(models.Model):
    _inherit = "res.company"
    invoice_logo = fields.Binary(string="Invoice Logo", readonly=False)
    thank_msg_img = fields.Binary(string="Thank you", readonly=False)
    invoice_format = fields.Selection([
        ('plain', 'Plain'),
        ('two_horizontal', 'Two Horizontal'),
        ('two_vertical', 'Two Vertical'),
        ('four_square', 'Four Square'),
        ('top1_bot2', 'Top One Bottom Two'),
        ('top2_bot1', 'Top Two Bottom One'),
        ('left1_right2', 'Left One Right Two'),
        ('left2_right1', 'Left Two Right One')
    ], default='four_square')
    image_invoice_1 = fields.Image("Image Invoice 1", max_width=512, max_height=512, store=True)
    image_invoice_2 = fields.Image("Image Invoice 2", max_width=512, max_height=512, store=True)
    image_invoice_3 = fields.Image("Image Invoice 3", max_width=512, max_height=512, store=True)
    image_invoice_4 = fields.Image("Image Invoice 4", max_width=512, max_height=512, store=True)

    @api.onchange('invoice_format')
    def change_invoice_format(self):
        self.image_invoice_1 = None
        self.image_invoice_2 = None
        self.image_invoice_3 = None
        self.image_invoice_4 = None

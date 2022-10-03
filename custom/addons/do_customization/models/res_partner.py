
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

    is_default = fields.Boolean('Default Vendor', default=False)
    delivery_person = fields.Boolean(string="Is a Delivery Person", help="Check this box if the contact is delivery person.", copy=False, track_visibility='onchange')


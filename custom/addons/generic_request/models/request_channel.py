import logging
from odoo import models, fields

_logger = logging.getLogger(__name__)


class RequestChannel(models.Model):
    _name = "request.channel"
    _description = "Request Channel"
    _inherit = [
        'generic.mixin.name_with_code',
        'generic.mixin.uniq_name_code',
        'generic.mixin.track.changes',
    ]
    _order = 'name, id'

    name = fields.Char(required=True, index=True)
    code = fields.Char()
    active = fields.Boolean(default=True, index=True)

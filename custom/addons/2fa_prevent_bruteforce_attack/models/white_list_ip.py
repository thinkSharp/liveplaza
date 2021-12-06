from odoo import fields, models, api


class WhiteListIp(models.Model):
    _name = 'white.list.ip'
    _description = 'White List Ip'

    ip = fields.Char(string="IP")

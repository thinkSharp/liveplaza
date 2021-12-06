from odoo import api, fields, models


class LogTimeLogin(models.Model):
    _name = 'log.time.login'

    check_login_fail_id = fields.Many2one(string="Login in Fail", comodel_name="check.login.fail")
    time = fields.Datetime(string="Login time")
    note = fields.Char(string="Note")

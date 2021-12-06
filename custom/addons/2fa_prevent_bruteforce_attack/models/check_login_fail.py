# -*- coding: utf-8 -*-

from odoo import models, fields, api
from datetime import datetime


class CheckLoginFail(models.Model):
    _name = 'check.login.fail'
    _description = 'Check Login Fail'

    name = fields.Char(string='User Name')
    ip_address = fields.Char(string='IP Address')
    state = fields.Selection(string='Status',
                             selection=[('active', 'active'), ('ban', 'Ban')],
                             compute="_compute_state", store=True)
    count = fields.Integer(string="Count Failed")

    log_time_ids = fields.One2many(comodel_name="log.time.login", string="Loging", inverse_name="check_login_fail_id")

    # @api.depends('count')
    # def _compute_state(self):
    #     for rec in self:
    #         rec.state = 'active'
    #         if rec.count >= 10:
    #             rec.state = 'ban'

    def reset_access(self):
        for rec in self:
            rec.sudo().write({
                'state': 'active',
                'count': 0,
            })
            self.env['log.time.login'].sudo().create({
                'time': datetime.now(),
                'note': 'Reset',
                'check_login_fail_id': rec.id
            })

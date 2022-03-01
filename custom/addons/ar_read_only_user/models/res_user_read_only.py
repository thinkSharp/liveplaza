# -*- coding: utf-8 -*-

from odoo import api, fields, models, tools,_
from odoo.exceptions import Warning

# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
import contextlib

import pytz
import datetime
import ipaddress
import itertools
import logging
import hmac

from collections import defaultdict
from hashlib import sha256
from itertools import chain, repeat
from lxml import etree
from lxml.builder import E
import passlib.context

from odoo import api, fields, models, tools, SUPERUSER_ID, _
from odoo.exceptions import AccessDenied, AccessError, UserError, ValidationError
from odoo.http import request
from odoo.osv import expression
from odoo.service.db import check_super
from odoo.tools import partition, collections, lazy_property

_logger = logging.getLogger(__name__)

USER_PRIVATE_FIELDS = []

DEFAULT_CRYPT_CONTEXT = passlib.context.CryptContext(
    # kdf which can be verified by the context. The default encryption kdf is
    # the first of the list
    ['pbkdf2_sha512', 'plaintext'],
    # deprecated algorithms are still verified as usual, but ``needs_update``
    # will indicate that the stored hash should be replaced by a more recent
    # algorithm. Passlib 1.6 supports an `auto` value which deprecates any
    # algorithm but the default, but Ubuntu LTS only provides 1.5 so far.
    deprecated=['plaintext'],
)

concat = chain.from_iterable

class ResUser(models.Model):
    _inherit = 'res.users'

    read_only = fields.Boolean(string="Make Read Only")
    ir_model_ids = fields.Many2many('ir.model', 'res_models_users_rel', 'user_id', 'model_id', string='Models for Write Access')
    str_model_list = fields.Char('Model List')
    
    @api.onchange('read_only')
    def set_read_only_user(self):
        read_only_grp_id = self.env['ir.model.data'].get_object_reference('ar_read_only_user', 'group_read_only_user')[1]
        if not self.read_only:
            self.read_only = True
            group_list = []
            for group in self.groups_id:
                group_list.append(group.id)
            group_list.append(read_only_grp_id)
            result= self.write({'groups_id':([(6,0,group_list)])})
        
        elif self.read_only:
            self.read_only = False
            group_list2 = []
            for group in self.groups_id:
                if group.id != read_only_grp_id: 
                    group_list2.append(group.id)
            result= self.write({'groups_id':([(6,0,group_list2)])})
            
    @api.model_create_multi
    def create(self, vals_list):

        ir_ms = self.env['ir.model']
        id_list = []
        namelist = []
        
        for one_d in vals_list:
            id_list = one_d.get("ir_model_ids")
            for data_s in id_list:
                for data in data_s[2]:
                    user_obj = self.env['ir.model'].browse(data)
                    namelist.append(user_obj.model)
            one_d["str_model_list"] = namelist
        print(vals_list)
        users = super(ResUser, self).create(vals_list)
        for user in users:
            # if partner is global we keep it that way
            if user.partner_id.company_id:
                user.partner_id.company_id = user.company_id
            user.partner_id.active = user.active
        return users

    def write(self, values):
        idr_list = []
        namelist = []
        
        if values.get('active') and SUPERUSER_ID in self._ids:
            raise UserError(_("You cannot activate the superuser."))
        if values.get('active') == False and self._uid in self._ids:
            raise UserError(_("You cannot deactivate the user you're currently logged in as."))

        if values.get('active'):
            for user in self:
                if not user.active and not user.partner_id.active:
                    user.partner_id.toggle_active()
        if self == self.env.user:
            for key in list(values):
                if not (key in self.SELF_WRITEABLE_FIELDS or key.startswith('context_')):
                    break
            else:
                if 'company_id' in values:
                    if values['company_id'] not in self.env.user.company_ids.ids:
                        del values['company_id']
                # safe fields only, so we write as super-user to bypass access rights
                self = self.sudo().with_context(binary_field_real_user=self.env.user)

        if values.get('ir_model_ids'):
            idr_list = values.get("ir_model_ids")
            for data_d in idr_list:
                for data in data_d[2]:
                    user_obj = self.env['ir.model'].browse(data)
                    namelist.append(user_obj.model)
            if namelist:
                values["str_model_list"] = namelist
            else:
                values["str_model_list"] = ''

        res = super(ResUser, self).write(values)
        if 'company_id' in values:
            for user in self:
                # if partner is global we keep it that way
                if user.partner_id.company_id and user.partner_id.company_id.id != values['company_id']:
                    user.partner_id.write({'company_id': user.company_id.id})

        if 'company_id' in values or 'company_ids' in values:
            # Reset lazy properties `company` & `companies` on all envs
            # This is unlikely in a business code to change the company of a user and then do business stuff
            # but in case it happens this is handled.
            # e.g. `account_test_savepoint.py` `setup_company_data`, triggered by `test_account_invoice_report.py`
            for env in list(self.env.envs):
                if env.user in self:
                    lazy_property.reset_all(env)

        # clear caches linked to the users
        if self.ids and 'groups_id' in values:
            # DLE P139: Calling invalidate_cache on a new, well you lost everything as you wont be able to take it back from the cache
            # `test_00_equipment_multicompany_user`
            self.env['ir.model.access'].call_cache_clearing_methods()
            self.env['ir.rule'].clear_caches()
            self.has_group.clear_cache(self)
        if any(key.startswith('context_') or key in ('lang', 'tz') for key in values):
            self.context_get.clear_cache(self)
        if any(key in values for key in ['active'] + USER_PRIVATE_FIELDS):
            db = self._cr.dbname
            for id in self.ids:
                self.__uid_cache[db].pop(id, None)
        if any(key in values for key in self._get_session_token_fields()):
            self._invalidate_session_cache()

        return res

class Journal_Import_Line(models.Model):
    _name = "ir.model.only"    

    line_id = fields.Many2one('res.users', string='Write Access Rights', ondelete="cascade")
    model_id = fields.Many2one('ir.model', string='Model', domain=[('transient', '=', False)], index=True, ondelete='cascade')
    mode_of_payment = fields.Char('Mode of Payment')
    ou_id = fields.Many2one('operating.unit', string='Operating Unit')

class IrModelAccess(models.Model):
    _inherit = 'ir.model.access'
    
    @api.model
    @tools.ormcache_context('self._uid', 'model', 'mode', 'raise_exception', keys=('lang',))
    def check(self, model, mode='read', raise_exception=True):
        result = super(IrModelAccess, self).check(model, mode, raise_exception=raise_exception)
        
        if not self._uid in (1,2,3,4,5,6,7,8):
            self._cr.execute(''' SELECT str_model_list FROM res_users WHERE id = %s''', [(self._uid)])
            model_list_data = self._cr.dictfetchone()
            if model_list_data:
                if model_list_data.get("str_model_list"):
                    for key,value in model_list_data.items():
                        if model not in value:
                            if self.env.user.has_group('ar_read_only_user.group_read_only_user'):
                                if mode != 'read':
                                    return False
                else:
                    if self.env.user.has_group('ar_read_only_user.group_read_only_user'):
                        if mode != 'read':
                            return False
        return result

class IrRule(models.Model):
    _inherit = 'ir.rule'

    def _compute_domain(self, model_name, mode="read"):
        res = super(IrRule,self)._compute_domain(model_name, mode)
        obj_list=['res.users.log','res.users','mail.channel','mail.alias','bus.presence','res.lang']

        if not self._uid in (1,2,3,4,5):
            self._cr.execute(''' SELECT str_model_list FROM res_users WHERE id = %s''', [(self._uid)])
            model_list_d = self._cr.dictfetchall()
            old_b = "[']"
            if model_list_d:
                model_list_daata = model_list_d[0]
                model_list_data = model_list_daata.get("str_model_list")
                for char in old_b:
                    model_list_data = model_list_data.replace(char, "")
                model_list_data = list(model_list_data.split(","))
                for value in model_list_data:
                    obj_list.append(value.strip())
        if model_name not in obj_list:
            if self.env.user.has_group('ar_read_only_user.group_read_only_user'):
                if mode != 'read':
                    raise Warning(_('Read only user can not done this operation..! (%s)') % self.env.user.name)
        return res
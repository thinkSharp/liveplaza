from odoo import models, fields, api, _
import logging
_logger = logging.getLogger(__name__)


PICK_DELI_DOMAIN_STRING = "get_pickup_deli_person_id()"

class IrActionWindow(models.Model):
    _inherit = 'ir.actions.act_window'

    def update_deli_dynamic_domain(self, res):
        if not res:
            return res
        obj_user = self.env.user
        try:
            for r in res:
                mp_dynamic_domain = r.get("domain", [])
                if mp_dynamic_domain and PICK_DELI_DOMAIN_STRING in mp_dynamic_domain:
                    domain_list = eval(mp_dynamic_domain)
                    list_of_index = [index for index, mp_tuple in enumerate(domain_list) if PICK_DELI_DOMAIN_STRING in str(mp_tuple[2])]
                    updated_domain = ""
                    if obj_user.has_group('base.group_system') or obj_user.has_group('access_rights_customization.group_operation_operator') or obj_user.has_group('access_rights_customization.group_operation_supervisor'):
                        for index in list_of_index:
                            var = domain_list[index][0]
                            if var == "id":
                                domain_list.pop(index)
                            else:
                                domain_list[index] =  (var,'!=', False)
                        updated_domain = str(domain_list)
                    elif obj_user.has_group('picking_and_delivery_vendor.pickup_vendor_group') or obj_user.has_group('picking_and_delivery_vendor.delivery_vendor_group'):
                        id_list = []
                        all_vendor_ids = self.env['res.partner'].search([('commercial_partner_id', '=', obj_user.partner_id.commercial_partner_id.id), ('active', '=', True)])
                        for id_d in all_vendor_ids:
                            id_list.append(id_d.id)

                        for index in list_of_index:
                            var = domain_list[index][0]
                            if var == "id":
                                domain_list[index] =  (var,'in', id_list)
                            else:
                                domain_list[index] =  (var,'!=', False)
                        updated_domain = str(domain_list)
                    else:
                        seller_id = obj_user.partner_id.id
                        for index in list_of_index:
                            var = domain_list[index][0]
                            if var == "id":
                                r["view_mode"] = "kanban,tree,form"
                                r["res_id"] = seller_id
                                r["views"] = [(self.env.ref('base.res_partner_kanban_view').id, "kanban"),(self.env.ref('do_customization.picking_method_in_partner_form_inherit').id, "form")]
                            domain_list[index] =  (var,'in', [seller_id])
                        updated_domain = str(domain_list)
                    if PICK_DELI_DOMAIN_STRING in (r.get('domain', '[]') or ''):
                        r['domain'] = updated_domain
        except Exception as e:
            _logger.info("~~~~~~~~~~Exception~~~~~~~~%r~~~~~~~~~~~~~~~~~",e)
            pass
        return res

    def read(self, fields=None, load='_classic_read'):
        res = super(IrActionWindow, self).read(fields=fields, load=load)
        return self.update_deli_dynamic_domain(res)

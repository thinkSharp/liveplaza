# -*- coding: utf-8 -*-
##########################################################################
#
#    Copyright (c) 2015-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>)
#
##########################################################################
import re
import base64
import logging
import uuid

from lxml import etree
from odoo.exceptions import Warning
from odoo import models, api, fields, _
from odoo.exceptions import ValidationError

_logger = logging.getLogger(__name__)


# OPERATOR =[
#     ('spin','Spin'),
#     ('darken','Darken'),
#     ('lighten','lighten'),
#     ('tint','Tint'),
#     ('shade','Shade'),
#     ('saturate','Saturate'),
#     ('desaturate','Desaturate'),
#     ('fadein','Fade In'),
#     ('fadeout','Fade Out'),
# ]


class Company(models.Model):
    _inherit= "res.company"

    favicon = fields.Binary()

class BackEndFont(models.Model):
    _name = "wk.backend.font"
    _description = "BackEnd Theme"

    name = fields.Char('Name', required=True, translate=True)
    active = fields.Boolean(default=True)
    default = fields.Boolean()
    family = fields.Char(required=True)
    # url = fields.Char()

    @api.model
    def create(self, vals):
        if vals.get('url') not in [None,False]:
            vals['url']=vals.get('url','').strip('/')
        if vals.get('family') not in [None,False]:
            vals['family'] =vals.get('family','').strip(';')
        return super(BackEndFont, self).create(vals)

    def write(self,vals):
        if vals.get('family') not in [None,False]:
            vals['family']=vals.get('family').strip(';')
        if vals.get('url') not in [None,False]:
            vals['url']=vals.get('url').strip('/')
        return super(BackEndFont, self).write(vals)

    @api.constrains('default')
    def _check_default(self):
        if len(self.search([('default', '=', True)])) > 1:
            raise ValidationError(_(
                "At a time only font can be  set as default !"))

class BackEndColor(models.Model):
    _name = "wk.backend.color"
    _description = "BackEnd Theme"

    name = fields.Char('Name', required=True, translate=True)
    active = fields.Boolean(default=True)
    default = fields.Boolean()
    color_primary = fields.Char(string='Primary Color')
    auto_color_secondary = fields.Boolean(string='Auto Calculate Secondary Color', help='Automatically calculate secondary color form primary color.')
    color_secondary = fields.Char(string='Secondary Color')
    # color_operator = fields.Selection(string='Color Perpetrator',selection=OPERATOR,default='spin')

    @api.model
    def create(self, vals):
        if vals.get('color_primary') not in [None,False]:
            vals['color_primary']=vals.get('color_primary','').strip(';')
        else:
            raise ValidationError('Primary Color required.')
        if vals.get('color_secondary') not in [None,False]:
            vals['color_secondary']=vals.get('color_secondary','').strip(';')

        return super(BackEndColor, self).create(vals)

    def write(self,vals):
        if vals.get('color_primary'):
            if vals.get('color_primary') not in [None,False]:
                vals['color_primary']=vals.get('color_primary','').strip(';')
            else:
                raise ValidationError('Primary Color required.')
        if vals.get('color_secondary') not in [None,False]:
            vals['color_secondary']=vals.get('color_secondary','').strip(';')

        return super(BackEndColor, self).write(vals)


    @api.constrains('default')
    def _check_default(self):
        if len(self.search([('default', '=', True)])) > 1:
            raise ValidationError(_(
                "At a time only color can be  set as default !"))

    # @api.model
    # def assign_color(self, color_id=None):
    #     self.env.user.write(dict(web_color_id=color_id))
    #     return True

    # @api.model
    # def assign_font(self, font_id=None):
    #     self.env.user.write(dict(web_font_id=font_id))
    #     return True


# class ResUsers(models.Model):
#     _inherit = "res.users"
#     web_color_id = fields.Many2one('wk.backend.color', string='Web Theme')
#     web_font_id = fields.Many2one('wk.backend.font', string='Web Font')

#     def __init__(self, pool, cr):
#         init_res = super(ResUsers, self).__init__(pool, cr)
#         self.SELF_WRITEABLE_FIELDS = list(self.SELF_WRITEABLE_FIELDS)
#         self.SELF_WRITEABLE_FIELDS.extend(['web_color_id'])
#         self.SELF_WRITEABLE_FIELDS.extend(['web_font_id'])

#         return init_res

class Assets(models.AbstractModel):
    _inherit = 'web_editor.assets'

    def save_asset_backend(self, url, bundle_xmlid, content, file_type):
        """
        Customize the content of a given asset (scss / js).

        Params:
            url (src):
                the URL of the original asset to customize (whether or not the
                asset was already customized)

            bundle_xmlid (src):
                the name of the bundle in which the customizations will take
                effect

            content (src): the new content of the asset (scss / js)

            file_type (src):
                either 'scss' or 'js' according to the file being customized
        """
        custom_url = self.make_custom_asset_file_url(url, bundle_xmlid)
        datas = base64.b64encode((content or "\n").encode("utf-8"))

        # Check if the file to save had already been modified
        custom_attachment = self._get_custom_attachment(custom_url)
        if custom_attachment:
            # If it was already modified, simply override the corresponding
            # attachment content
            custom_attachment.write({"datas": datas})
        else:
            # If not, create a new attachment to copy the original scss/js file
            # content, with its modifications
            new_attach = {
                'name': url.split("/")[-1],
                'type': "binary",
                'mimetype': (file_type == 'js' and 'text/javascript' or 'text/scss'),
                'datas': datas,
                'url': custom_url,
            }
            # new_attach.update(self._save_asset_attachment_hook())
            res = self.env["ir.attachment"].create(new_attach)
            # Create a view to extend the template which adds the original file
            # to link the new modified version instead
            file_type_info = {
                'tag': 'link' if file_type == 'scss' else 'script',
                'attribute': 'href' if file_type == 'scss' else 'src',
            }

            def views_linking_url(view):
                """
                Returns whether the view arch has some html tag linked to
                the url. (note: searching for the URL string is not enough as it
                could appear in a comment or an xpath expression.)
                """
                tree = etree.XML(view.arch)
                return bool(tree.xpath("//%%(tag)s[@%%(attribute)s='%(url)s']" % {
                    'url': url,
                } % file_type_info))

            IrUiView = self.env["ir.ui.view"]
            view_to_xpath = IrUiView.get_related_views(bundle_xmlid, bundles=True).filtered(views_linking_url)
            new_view = {
                'name': custom_url,
                'key': 'web_editor.%s_%s' % (file_type, str(uuid.uuid4())[:6]),
                'mode': "extension",
                'inherit_id': view_to_xpath.id,
                'arch': """
                    <data inherit_id="%(inherit_xml_id)s" name="%(name)s">
                        <xpath expr="//%%(tag)s[@%%(attribute)s='%(url_to_replace)s']" position="attributes">
                            <attribute name="%%(attribute)s">%(new_url)s</attribute>
                        </xpath>
                    </data>
                """ % {
                    'inherit_xml_id': view_to_xpath.xml_id,
                    'name': custom_url,
                    'url_to_replace': url,
                    'new_url': custom_url,
                } % file_type_info
            }

            # TODO
            # Remove this method
            # _save_asset_view_hook
            # No need for this
            new_view.update(self._save_asset_view_hook())
            view_id = IrUiView.create(new_view)
            view_id.website_id = False
        self.env["ir.qweb"].clear_caches()

    def _generate_updated_file_content(self, updatedFileContent, name, value):
        pattern = "'%s': %%s,\n" % name
        regex = re.compile(pattern % ".+")
        replacement = pattern % value
        if regex.search(updatedFileContent):
            updatedFileContent = re.sub(regex, replacement, updatedFileContent)
        else:
            updatedFileContent = re.sub(r'( *)(.*hook.*)', r'\1%s\1\2' % replacement, updatedFileContent)
        return updatedFileContent

    def make_scss_customization_backend(self, url, value, style_type, **kw):
        """
        Makes a scss customization of the given file. That file must
        contain a scss map including a line comment containing the word 'hook',
        to indicate the location where to write the new key,value pairs.

        Params:
            url (str):
                the URL of the scss file to customize (supposed to be a variable
                file which will appear in the assets_common bundle)

            values (dict):
                key,value mapping to integrate in the file's map (containing the
                word hook). If a key is already in the file's map, its value is
                overridden.
        """
        custom_url = self.make_custom_asset_file_url(url, 'web.assets_backend')
        updatedFileContent = self.get_asset_content(custom_url) or self.get_asset_content(url)
        updatedFileContent = updatedFileContent.decode('utf-8')
        if style_type == 'color':
            values = {
                'primary_color': value
            }
            color_id = kw.get('id', False)
            if color_id:
                color_id = self.env['wk.backend.color'].search([('id','=', color_id)])
                default_color_id = self.env['wk.backend.color'].search([('default','=', True)])
                if default_color_id:
                    default_color_id.default = False
                color_id.default = True
                #Default Color value
                secondary_color = value

                is_auto = color_id.auto_color_secondary
                if not is_auto:
                    secondary_color = color_id.color_secondary
                else:
                    secondary_color = 'complement(' + value + ')'
                values.update({
                    'secondary_color': secondary_color
                })
            for name, value in values.items():
                updatedFileContent = self._generate_updated_file_content(updatedFileContent, name, value)
        else:
            font_id = self.env['wk.backend.font'].browse([int(kw.get('id'))])
            default_font_id = self.env['wk.backend.font'].search([('default','=', True)])
            if default_font_id:
                default_font_id.default = False
            font_id.default = True
            family = '+'.join(font_id.family.strip().split(',')[0].strip().split(' '))
            values = {
                'font': value.split(',')[0],
                'family': family
            }
            for name, value in values.items():
                updatedFileContent = self._generate_updated_file_content(updatedFileContent, name, value)
        self.save_asset_backend(url, 'web.assets_backend', updatedFileContent, 'scss')


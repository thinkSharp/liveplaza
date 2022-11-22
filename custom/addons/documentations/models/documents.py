from odoo import api, fields, models, _
from odoo.exceptions import ValidationError
from odoo.addons.http_routing.models.ir_http import slug
from odoo.http import request


class DocumentCategory(models.Model):
    _name = "documents.category"
    _description = "Documents Category"
    _order = "sequence"

    name = fields.Char(string=" Category Name", required=True)
    name_myanmar = fields.Char(string="Myanmar Category Name")
    display_name = fields.Char(string="Display Name", compute="_compute_display_name")
    sequence = fields.Float(string="Sequence", default=30)
    website_published = fields.Boolean(stirng="Published", copy=False, default=True)
    parent_id = fields.Many2one('documents.category', string="Parent Category")
    child_id = fields.One2many('documents.category', 'parent_id', 'Child Categories', readonly=True)
    child_documents = fields.One2many('documents', 'category', 'Child Documents', readonly=True)

    def toggle_website_published(self):
        """ Inverse the value of the field ``website_published`` on the records in ``self``. """
        for record in self:
            record.website_published = not record.website_published

    @api.constrains('sequence')
    def _check_value(self):
        if self.sequence <= 0:
            raise ValidationError(_('Enter the sequence value greater than 0'))

    @api.depends('name', 'parent_id.display_name')  # this definition is recursive
    def _compute_display_name(self):
        for cat in self:
            if cat.parent_id:
                cat.display_name = cat.parent_id.display_name + ' / ' + cat.name
            else:
                cat.display_name = cat.name

    @api.constrains('parent_id')
    def check_parent_id(self):
        if not self._check_recursion():
            raise ValidationError(_('Error ! You cannot create recursive categories.'))


class Documents(models.Model):
    _name = "documents"
    _description = "User Guides Documentation"
    _order = "sequence"

    name = fields.Char(string="Name", required=True)
    name_myanmar = fields.Char(string="Myanmar Document Name")
    description = fields.Text(string="Description")
    category = fields.Many2one("documents.category", string="Category", required=True)
    sequence = fields.Float(string="Sequence", default=30)
    document_lines = fields.One2many("documents.line", "line_id", string="Documents Text", ondelete='cascade')
    website_published = fields.Boolean(stirng="Published", copy=False, default=True)
    video = fields.Binary(string="Guide Video")
    action_id = fields.Many2many('ir.actions.act_window', string='Action')

    def toggle_website_published(self):
        """ Inverse the value of the field ``website_published`` on the records in ``self``. """
        for record in self:
            record.website_published = not record.website_published

    @api.constrains('sequence')
    def _check_value(self):
        if self.sequence <= 0:
            raise ValidationError(_('Enter the sequence value greater than 0'))


class DocumentsLine(models.Model):
    _name = "documents.line"
    _description = "Documents Line"
    _order = "sequence"

    name = fields.Char(string="Name", required=True)
    title = fields.Html(string="Title")
    text = fields.Html(string="Text body")
    name_myanmar = fields.Char(string="Myanmar Language Name")
    title_myanmar = fields.Html(string="Myanmar Language Title")
    text_myanmar = fields.Html(string="Myanmar Language Text body")
    image_1 = fields.Image(string="Image")
    add_line = fields.Boolean("Add a border under document line")
    sequence = fields.Float(string="Sequence", default=30)
    line_id = fields.Many2one('documents', string="Line Id")

    def toggle_website_published(self):
        """ Inverse the value of the field ``website_published`` on the records in ``self``. """
        for record in self:
            record.website_published = not record.website_published

    @api.constrains('sequence')
    def _check_value(self):
        for record in self:
            if record.sequence <= 0:
                raise ValidationError(_('Enter the sequence value greater than 0'))

    @api.constrains('image_width')
    def _set_image_width(self):
        for record in self:
            if record.image_1 and record.image_width < 20:
                record.image_width = 50.0


class Website(models.Model):
    _inherit = 'website'

    # @staticmethod
    def _get_documents_url(self, category, sub_category=None, doc=None):
        url = "user_guides/"
        if category:
            url = "/user_guides/%s" % slug(category)
            if sub_category:
                self._get_parent_categ_route(sub_category)
                url = "/user_guides/sub" + "/%s" % slug(sub_category)
            elif doc:
                url = "/user_guides/%s" % slug(category) + "/%s" % slug(doc)
        return url

    @staticmethod
    def _get_translate_text(field, myanmar=False, field_type="name"):
        if field_type == "title":
            if myanmar and field.title_myanmar:
                return field.title_myanmar
            else:
                return field.title
        if field_type == "text":
            if myanmar and field.text_myanmar:
                return field.text_myanmar
            else:
                return field.text

        if myanmar and field.name_myanmar:
            return field.name_myanmar
        else:
            return field.name

    @staticmethod
    def _check_category_has_child(categ):
        if categ.child_id:
            for c in categ.child_id:
                if c.website_published:
                    return True
        return False

    # to show breadcrumbs
    @staticmethod
    def _get_parent_categ_route(category):
        parent_categ = []
        parent_route = []
        temp_categ = category
        while temp_categ.parent_id:
            parent_categ.append(temp_categ)
            temp_categ = temp_categ.parent_id

        i = 0
        while i < len(parent_categ):
            if parent_categ[i].parent_id and parent_categ[i].parent_id.parent_id:
                parent_route.append(parent_categ[i])
            i += 2

        parent_route.reverse()
        return parent_route

    # @staticmethod
    def _get_all_breadcrumbs(self, category=None, count=0):
        breadcrumbs_list = {'LIVEPlaza': '/home', 'User Guides': '/user_guides'}
        if category:
            parent_route = self._get_parent_categ_route(category)
            for p in parent_route:
                breadcrumbs_list[p.name] = self._get_documents_url(p.parent_id, sub_category=p)
            if count > 0:
                length = len(breadcrumbs_list) - count
                if length > 0:
                    breadcrumbs_limit = {}
                    i = 0;
                    for k, v in breadcrumbs_list.items():
                        if i >= length:
                            breadcrumbs_limit[k] = v
                        i += 1
                    return breadcrumbs_limit
        return breadcrumbs_list




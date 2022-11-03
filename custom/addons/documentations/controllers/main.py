from odoo import http, tools
from odoo.http import request, route
from odoo.tools.misc import formatLang, format_date, get_lang
import logging
from odoo.osv import expression

_logger = logging.getLogger(__name__)


class UserGuides(http.Controller):
    def _get_search_doc_domain(self, search):
        domains = []
        if search:
            for srch in search.split(" "):
                subdomains = [
                    [('title', 'ilike', srch)],
                    [('text', 'ilike', srch)],
                    [('title_myanmar', 'ilike', srch)],
                    [('text_myanmar', 'ilike', srch)]
                ]
                domains.append(expression.OR(subdomains))
            domains.append([])
        return expression.AND(domains)
        # return domains

    @staticmethod
    def _check_child_has_child(category):
        result = False
        for categ in category.child_id:
            if categ.child_id:
                result = True
        return result

    @http.route('/user_guides', type='http', auth='public', website=True)
    def user_guides(self, search='', search_filter='', lang=None, **post):
        documents = request.env['documents'].search([('website_published', '=', True)])
        documents_categ = request.env['documents.category'].search([('website_published', '=', True)])
        lang = get_lang(request.env)

        domain = [('website_published', '=', True)]

        if "burmese" in lang.name.lower() or "myanmar" in lang.name.lower():
            myanmar = True
        else:
            myanmar = False

        # search features (new template for search view)
        if search:
            line_domain = self._get_search_doc_domain(search)
            search_doc_line = request.env['documents.line'].search(line_domain)
            search_doc_group = {doc: {} for doc in documents}  # initialize empty doc -> doc_lines dictionary

            # initialize empty doc_categ -> doc_lines dictionary
            search_categ_group = {categ: {} for categ in documents_categ}

            # group the search doc lines by doc
            for doc in documents:
                search_doc_line_list = []
                for s_doc in search_doc_line:
                    if s_doc in doc.document_lines:
                        search_doc_line_list.append(s_doc)
                search_doc_group[doc] = search_doc_line_list

            # group search doc lines from search_doc_group by categ
            for categ in search_categ_group:
                for doc in search_doc_group:
                    if doc.category.id == categ.id:
                        if len(search_categ_group[categ]) > 0:
                            search_categ_group[categ] += search_doc_group[doc]
                        else:
                            search_categ_group[categ] = search_doc_group[doc]

            # total search document lines count
            search_count = 0
            for doc in search_categ_group.values():
                search_count += len(doc)

            search_filter_doc = []
            if search_filter:
                for categ, doc in search_categ_group.items():
                    new_filter = search_filter.split('_')

                    if new_filter:
                        search_filter = new_filter[0]
                        if str(categ.id) == new_filter[0]:
                            search_filter_doc = doc
                            search_count = len(search_filter_doc)

            values = {
                'docs_categories': documents_categ,
                'docs': documents,
                'myanmar': myanmar,
                'domain': domain,
                'search': search,
                'search_docs': search_categ_group,
                'search_count': search_count,
                'search_doc_line': search_doc_line,
                'search_filter': search_filter,
                'search_filter_doc': search_filter_doc,
                'page_name': 'user_guides_search',
            }
            return request.render("documentations.documents_search_view", values)

        values = {
            'docs_categories': documents_categ,
            'docs': documents,
            'myanmar': myanmar,
            'domain': domain,
            'page_name': 'User Guides',
        }
        return request.render("documentations.user_guides", values)

    @http.route('/user_guides/sub/<model("documents.category"):sub_category>',
                type='http', auth='public', website=True)
    def user_guides_sub_categories(self, category='', sub_category=''):
        has_child = self._check_child_has_child(sub_category)

        lang = get_lang(request.env)
        if "burmese" in lang.name.lower() or "myanmar" in lang.name.lower():
            myanmar = True
        else:
            myanmar = False

        values = {
            'categ': category,
            'sub_category': sub_category,
            'has_child': has_child,
            'page_name': sub_category.name,
            'myanmar': myanmar,
        }
        return request.render("documentations.user_guides_sub_categories", values)

    @http.route(['/user_guides/<model("documents.category"):category>',
                 '/user_guides/<model("documents.category"):category>/<model("documents"):document>/'
                 ],
                type='http', auth='public', website=True)
    def documentations(self, category='', document=''):
        lang = get_lang(request.env)
        if "burmese" in lang.name.lower() or "myanmar" in lang.name.lower():
            myanmar = True
        else:
            myanmar = False

        values = {
            'category': category,
            'documents': category.child_documents,
            'document': document,
            # 'doc_line': line,
            'page_name': 'documentations',
            'myanmar': myanmar,
        }
        return request.render("documentations.documentations", values)

import os
import requests
import lxml.html

from odoo import models, api, _
from odoo.exceptions import UserError

PRINT_PDF_SERVICE_URL = os.environ.get('PRINT_PDF_SERVICE_URL')
match_klass = "//div[contains(concat(' ', normalize-space(@class), ' '), ' {} ')]"

def get_div_with_klass(html, klass):
  doc = lxml.html.document_fromstring(html)
  el = doc.xpath(match_klass.format(klass))
  if len(el) > 0:
    return lxml.html.tostring(el.pop(0))
  else:
    return b''

class IrActionsReport(models.Model):
  _name = 'ir.actions.report'
  _inherit = 'ir.actions.report'


  @api.model
  def get_wkhtmltopdf_state(self):
    if PRINT_PDF_SERVICE_URL:
      return 'ok'
    else:
      return super(IrActionsReport, self).get_wkhtmltopdf_state()

  @api.model
  def _run_wkhtmltopdf(self, bodies, header=None, footer=None, landscape=False, specific_paperformat_args=None, set_viewport_size=False):
    if PRINT_PDF_SERVICE_URL:
      return self._print_on_service(bodies, header, footer, landscape, specific_paperformat_args, set_viewport_size)
    else:
      return super(IrActionsReport, self)._run_wkhtmltopdf(bodies, header, footer, landscape, specific_paperformat_args, set_viewport_size)

  @api.model
  def _print_on_service(self, bodies, header=None, footer=None, landscape=False, specific_paperformat_args=None, set_viewport_size=False):
    files = []
    for b in bodies:
      files.append(('contents', b))

    paperformat_id = self.get_paperformat()

    data = self._build_print_service_options(paperformat_id, landscape, specific_paperformat_args=specific_paperformat_args)

    if header:
      header = get_div_with_klass(header, 'header')
      data.setdefault("header", header)

    if footer:
      footer = get_div_with_klass(footer, 'footer')
      data.setdefault("footer", footer)

    try:
      response = requests.post(PRINT_PDF_SERVICE_URL, data=data, files=files)
      if response.status_code == 200:
        return response.content
      else:
        raise UserError(_("Something went wrong while printing pdf. Please contact to your developer team."))
    except requests.exceptions.ConnectionError:
      raise UserError(_("Make sure pdf printing server is running."))

  @api.model
  def _build_print_service_options(self, paperformat_id, landscape, specific_paperformat_args=None):

    data = {
      "printBackground": "true"
    }

    if paperformat_id.format and paperformat_id.format != 'custom':
      data.setdefault("format", paperformat_id.format)

    if paperformat_id.page_width and paperformat_id.page_height and paperformat_id.format == 'custom':
      data.setdefault("width", paperformat_id.page_width)
      data.setdefault("height", paperformat_id.page_height)

    if specific_paperformat_args and specific_paperformat_args.get('data-report-margin-top'):
      margin_top = specific_paperformat_args.get('data-report-margin-top')
    else:
      margin_top = paperformat_id.margin_top

    margin_top = str(margin_top)
    margin_bottom = str(paperformat_id.margin_bottom)
    margin_left = str(paperformat_id.margin_left)
    margin_right = str(paperformat_id.margin_right)

    data.setdefault("marginTop", margin_top)
    data.setdefault("marginBottom", margin_bottom)
    data.setdefault("marginLeft", margin_left)
    data.setdefault("marginRight", margin_right)

    if landscape is None and specific_paperformat_args and specific_paperformat_args.get('data-report-landscape'):
      landscape = specific_paperformat_args.get('data-report-landscape')

    if landscape:
      data.setdefault("landscape", "true")
    elif str(paperformat_id.orientation).lower() == 'landscape':
      data.setdefault("landscape", "true")
    else:
      data.setdefault("landscape", "false")

    return data

import os
import os.path
import json
from odoo import http
from odoo.http import Controller, request

__location__ = os.path.realpath(
  os.path.join(os.getcwd(), os.path.dirname(__file__))
)

class CelebrityNewsController(Controller):

  @http.route('/celebrity_news', type='http', auth='public', website=True)
  def celebrity_news(self, **post):
    news = self.load_news()
    return request.render("celebrity_news.celebrity_news", {
      "news": news
    })

  def load_news(self):
    data_path = os.path.join(__location__, "../data/news.json")
    with open(data_path, 'r') as f:
      news = json.load(f)
      return news

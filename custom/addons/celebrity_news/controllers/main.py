from odoo import http
from odoo.http import Controller, request

NEWS = [
  {
    'title': "Businesses don't like using my medicine and expensive...Khin Chan Myae Thu",
    'srcset': "https://alpscreations-images.s3.ap-southeast-1.amazonaws.com/small_0_02_06_a1d82cbf118bd02ade8a60658b1832c21b681259b548cdfb4c159bcb040a0f74_b6dca78b5c21429c_0d75397cb6.jpg 1x, https://alpscreations-images.s3.ap-southeast-1.amazonaws.com/small_0_02_06_a1d82cbf118bd02ade8a60658b1832c21b681259b548cdfb4c159bcb040a0f74_b6dca78b5c21429c_0d75397cb6.jpg 2x",
    'src': "https://alpscreations-images.s3.ap-southeast-1.amazonaws.com/small_0_02_06_a1d82cbf118bd02ade8a60658b1832c21b681259b548cdfb4c159bcb040a0f74_b6dca78b5c21429c_0d75397cb6.jpg",
    'info': "7 views . 4 days ago",
    'url': "https://alpscreations.tv/feeds/134",
  },
  {
    'title': "An interest in the gold suit and the audience... Ye Lay Ma",
    'srcset': "https://alpscreations-images.s3.ap-southeast-1.amazonaws.com/small_0_02_06_39feb1ddaddf4cbe771e51e3d69511e303321f3ef28b122b26318baf89f43cca_d3b69fe8466db3a2_6cb62b9788.jpg 1x, https://alpscreations-images.s3.ap-southeast-1.amazonaws.com/small_0_02_06_39feb1ddaddf4cbe771e51e3d69511e303321f3ef28b122b26318baf89f43cca_d3b69fe8466db3a2_6cb62b9788.jpg 2x",
    'src': "https://alpscreations-images.s3.ap-southeast-1.amazonaws.com/small_0_02_06_39feb1ddaddf4cbe771e51e3d69511e303321f3ef28b122b26318baf89f43cca_d3b69fe8466db3a2_6cb62b9788.jpg",
    'info': "4 views . 4 days ago",
    'url': "https://alpscreations.tv/feeds/133",
  },
  {
    'title': "I'm a single mom but I want to be a dignified blogger",
    'srcset': "https://alpscreations-images.s3.ap-southeast-1.amazonaws.com/small_0_02_06_bbceb20bccb013e74f39813c0d129d802d500c3501df48afb9fd909004a7c737_5e99ad2171b1514c_931fa70892.jpg 1x, https://alpscreations-images.s3.ap-southeast-1.amazonaws.com/small_0_02_06_bbceb20bccb013e74f39813c0d129d802d500c3501df48afb9fd909004a7c737_5e99ad2171b1514c_931fa70892.jpg 2x",
    'src': "https://alpscreations-images.s3.ap-southeast-1.amazonaws.com/small_0_02_06_bbceb20bccb013e74f39813c0d129d802d500c3501df48afb9fd909004a7c737_5e99ad2171b1514c_931fa70892.jpg",
    'info': "1 views . 4 days ago",
    'url': "https://alpscreations.tv/feeds/132",
  },
  {
    'title': "I am happy that the success of The Marriage movie is... Kyaw Htet Aung",
    'srcset': "https://alpscreations-images.s3.ap-southeast-1.amazonaws.com/small_0_02_06_bd62460e8392fb45f48b64ee31988dc484740a50be044cfdac2bfde852038774_9eb729c0bee5ca37_2c78451d7b.jpg 1x, https://alpscreations-images.s3.ap-southeast-1.amazonaws.com/small_0_02_06_bd62460e8392fb45f48b64ee31988dc484740a50be044cfdac2bfde852038774_9eb729c0bee5ca37_2c78451d7b.jpg 2x",
    'src': "https://alpscreations-images.s3.ap-southeast-1.amazonaws.com/small_0_02_06_bd62460e8392fb45f48b64ee31988dc484740a50be044cfdac2bfde852038774_9eb729c0bee5ca37_2c78451d7b.jpg",
    'info': "0 views . 4 days ago",
    'url': "https://alpscreations.tv/feeds/131",
  },
  {
    'title': "I've tried many times...They were pulled out...Htet Htet Htun",
    'srcset': "https://alpscreations-images.s3.ap-southeast-1.amazonaws.com/small_0_02_06_f0389da433b9b0b9bb378327229b67d0d082bb3abacb8b6493386880f48fd4ac_b3e4a13d754f3555_8b415c8928.jpg 1x, https://alpscreations-images.s3.ap-southeast-1.amazonaws.com/small_0_02_06_f0389da433b9b0b9bb378327229b67d0d082bb3abacb8b6493386880f48fd4ac_b3e4a13d754f3555_8b415c8928.jpg 2x",
    'src': "https://alpscreations-images.s3.ap-southeast-1.amazonaws.com/small_0_02_06_f0389da433b9b0b9bb378327229b67d0d082bb3abacb8b6493386880f48fd4ac_b3e4a13d754f3555_8b415c8928.jpg",
    'info': "1 views . 4 days ago",
    'url': "https://alpscreations.tv/feeds/130",
  },
  {
    'title': "I was injured while traveling at sea..I don't like the sea very much..I feel hot... May Mi Ko Ko",
    'srcset': "https://alpscreations-images.s3.ap-southeast-1.amazonaws.com/small_0_02_06_4e929f100ef823737fee5aacb1af270e2d412e13ec1d6f9bed086cdf6498c3f5_d541b8e41b50dada_011a243bd4.jpg 1x, https://alpscreations-images.s3.ap-southeast-1.amazonaws.com/small_0_02_06_4e929f100ef823737fee5aacb1af270e2d412e13ec1d6f9bed086cdf6498c3f5_d541b8e41b50dada_011a243bd4.jpg 2x",
    'src': "https://alpscreations-images.s3.ap-southeast-1.amazonaws.com/small_0_02_06_4e929f100ef823737fee5aacb1af270e2d412e13ec1d6f9bed086cdf6498c3f5_d541b8e41b50dada_011a243bd4.jpg",
    'info': "1 views . 4 days ago",
    'url': "https://alpscreations.tv/feeds/129",
  },
  {
    'title': "When I was young I'm bad, So they pulled my ears and my ears were not pretty",
    'srcset': "https://alpscreations-images.s3.ap-southeast-1.amazonaws.com/small_0_02_06_a6019843ed813a71f93b24a6b6ebfe5f29635f281e3721135b05e8982117c253_72ffa8fbcc65d95c_cae64ef630.jpg 1x, https://alpscreations-images.s3.ap-southeast-1.amazonaws.com/small_0_02_06_a6019843ed813a71f93b24a6b6ebfe5f29635f281e3721135b05e8982117c253_72ffa8fbcc65d95c_cae64ef630.jpg 2x",
    'src': "https://alpscreations-images.s3.ap-southeast-1.amazonaws.com/small_0_02_06_a6019843ed813a71f93b24a6b6ebfe5f29635f281e3721135b05e8982117c253_72ffa8fbcc65d95c_cae64ef630.jpg",
    'info': "10 views . 7 days ago",
    'url': "https://alpscreations.tv/feeds/128",
  },
  {
    'title': "We will support those affected by the Mokha storm... Soe Myat Thuzar &amp; Khine Hnin Wai",
    'srcset': "https://alpscreations-images.s3.ap-southeast-1.amazonaws.com/small_0_02_01_46c8b2d7c41e275a56257ea1244e273518ed18c5f6b11bb07431654c09cdad7a_916d5e7e59c28163_69222e9f9b.jpg 1x, https://alpscreations-images.s3.ap-southeast-1.amazonaws.com/small_0_02_01_46c8b2d7c41e275a56257ea1244e273518ed18c5f6b11bb07431654c09cdad7a_916d5e7e59c28163_69222e9f9b.jpg 2x",
    'src': "https://alpscreations-images.s3.ap-southeast-1.amazonaws.com/small_0_02_01_46c8b2d7c41e275a56257ea1244e273518ed18c5f6b11bb07431654c09cdad7a_916d5e7e59c28163_69222e9f9b.jpg",
    'info': "2 views . 7 days ago",
    'url': "https://alpscreations.tv/feeds/127",
  },
  {
    'title': "There is a request for Ma Ma Song for one hundred and fifty thousand",
    'srcset': "https://alpscreations-images.s3.ap-southeast-1.amazonaws.com/small_0_02_06_dcf9fcd263cbc0c250f6af31ee561b0047eb76d7f8fc338ca81bed2a754b2efd_753b5468d4e983b_fd8d48929a.jpg 1x, https://alpscreations-images.s3.ap-southeast-1.amazonaws.com/small_0_02_06_dcf9fcd263cbc0c250f6af31ee561b0047eb76d7f8fc338ca81bed2a754b2efd_753b5468d4e983b_fd8d48929a.jpg 2x",
    'src': "https://alpscreations-images.s3.ap-southeast-1.amazonaws.com/small_0_02_06_dcf9fcd263cbc0c250f6af31ee561b0047eb76d7f8fc338ca81bed2a754b2efd_753b5468d4e983b_fd8d48929a.jpg",
    'info': "3 views . 7 days ago",
    'url': "https://alpscreations.tv/feeds/126",
  },
]

class CelebrityNewsController(Controller):

  @http.route('/celebrity_news', type='http', auth='public', website=True)
  def celebrity_news(self, **post):
    return request.render("celebrity_news.celebrity_news", {
      "news": NEWS
    })

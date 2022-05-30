import odoo
import os
import re,pickle
from odoo import fields, models, http, api
import logging
_logger=logging.getLogger(__name__)
from odoo import http
import requests
from odoo.http import root
# import http_patch

class ResConfigSettingsRedis(models.TransientModel):

    _inherit = 'res.config.settings'


    def button_convert_werkzeug_to_redis(self):
        session=root.session_store

        if hasattr(session,'redis'):
            path=odoo.tools.config.session_dir
            for fname in os.listdir(path):
                path_1 = os.path.join(path, fname)
                try:
                    try:
                        f = open(path_1, 'rb')
                    except IOError:
                        data = {}
                    else:
                        try:
                            try:
                                data = pickle.load(f)
                            except Exception:
                                data = {}
                        finally:
                            f.close()
                        session_key=re.sub('\.sess$', '', fname)
                        session.redis.set(session_key,pickle.dumps(data),ex=session.expire)
                    os.unlink(path_1)
                except OSError:
                    pass
        else:
            _logger.debug("!!! This button will work only when sessions are stores in Redis !!!")

# -*- coding: utf-8 -*-
#################################################################################
#
#    Copyright (c) 2015-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>)
#
#################################################################################
# PLEASE REFER THE FOLLOWING DOCS - https://buildmedia.readthedocs.org/media/pdf/redis-py-cluster/unstable/redis-py-cluster.pdf
import os
import time
import sys
from odoo import http,tools
import logging
import werkzeug.contrib.sessions
_logger=logging.getLogger(__name__)
from werkzeug.contrib.sessions import SessionStore,Session
from odoo.http import Root,OpenERPSession
from odoo.tools.func import lazy_property
import odoo
import pickle
import random
REDIS_STATUS = False
import re
try:
    import redis
    # from rediscluster import RedisCluster
    REDIS_STATUS = True
except:
    _logger.info("< ERROR : Redis not found in server, run camand pip install redis. >")

# REDIS_ENABLE = False

class RedissystemSessionStore(SessionStore):

    def __init__(self,host,port,expire,db, ssl_ca_certs,session_class=None,redis_key_template='werkzeug_%s'):
        SessionStore.__init__(self, session_class)
        self.port = port
        self.host = host
        self.db = db
        self.redis_key_template = redis_key_template
        self.ssl_ca_certs = ssl_ca_certs
        self.redis = self._getRedisObj()
        self.expire=expire

    def _getRedisObj(self):
        try:
            redisObj = redis.Redis(
            host = self.host,
            port = self.port,
            db   = self.db,
            ssl  = self.ssl_ca_certs and True or False,
            ssl_ca_certs = self.ssl_ca_certs or None,
            )
            # startup_nodes = [
            #     {
            #         "host": self.host,
            #         "port": self.port,
            #         "ssl" : self.ssl_ca_certs and True or False,
            #         "ssl_ca_certs" : self.ssl_ca_certs or None,
            #         }
            #     ]
            # redisObj = RedisCluster(startup_nodes=startup_nodes, decode_responses=False, skip_full_coverage_check=True)
            redisObj.ping()
            _logger.debug('REDIS CONNECTION SUCCESSFULL !! HURRAY ENJOY :)')
            return redisObj
        except Exception as e:
            _logger.error('REDIS CONNECTION EXCEPTION : %r',e)
            return False

    def save(self, session):
        try:
            fn1 = self._saveRedisSession(session)
        except Exception as e:
            _logger.debug('%r',e)

    def _renameSessionKey(self,sid):
        return (self.redis_key_template % sid)
        # return sid

    def _saveRedisSession(self, session):
        session_key=self._renameSessionKey(session.sid)
        return self.redis.set(session_key,pickle.dumps(dict(session)),ex=self.expire)


    def get(self, sid):

        try:
            data = self._getRedisKey(sid)
            redis_key = self._renameSessionKey(sid)
            self.redis.set(redis_key,data,ex=self.expire)
            data = pickle.loads(data)
        except:
            data= {}
        return self.session_class(data, sid, False)

    def _getRedisKey(self,sid):
        session_key=self._renameSessionKey(sid)
        return self.redis.get(session_key)

    def delete(self, session):
        try:
            fn1 = self.redis.delete(session.sid)
        except Exception as e:
            _logger.debug('%r',e)

# http.RedissystemSessionStore = RedissystemSessionStore

@lazy_property
def session_store(self):
    # Setup http sessions
    if tools.config.get('redis_session') and REDIS_STATUS:
        host = tools.config.get('redis_host') or 'localhost'
        port = tools.config.get('redis_port') or 6379
        expire = tools.config.get('redis_expire') or 60 * 60 * 24 * 5 # Expire in 5 days
        ssl_ca_certs = tools.config.get('redis_ssl_ca_certs') or None
        session = RedissystemSessionStore(session_class = OpenERPSession,
                                          host = host,
                                          port = port,
                                          expire = expire,
                                          ssl_ca_certs = ssl_ca_certs,
                                          db=0
                                          )
        # REDIS_ENABLE = True
    else:
        path = odoo.tools.config.session_dir
        _logger.debug('HTTP sessions stored in: %s', path)
        session = werkzeug.contrib.sessions.FilesystemSessionStore(path, session_class=OpenERPSession)
    return session

http.Root.session_store = session_store


def session_gc(session_store):
    if not hasattr(session_store,'redis'):
        if random.random() < 0.001:
            # we keep session one week
            last_week = time.time() - 60*60*24*7
            for fname in os.listdir(session_store.path):
                path = os.path.join(session_store.path, fname)
                try:
                    if os.path.getmtime(path) < last_week:
                        os.unlink(path)
                except OSError:
                    pass
    else:
        # because sessions store in REDIS
        pass

http.session_gc = session_gc

#!/usr/bin/env python
#
# @name: api/base.py
# @create: Aug. 21th, 2014
# @update: Aug. 21th, 2014
# @author: hitigon@gmail.com
import tornado.web
from mongoengine.connection import get_db
from oauthlib.oauth2 import Server
from oauth.validator import OAuth2Validator


class BaseHandler(tornado.web.RequestHandler):

    def initialize(self):
        self.db = get_db()
        validator = OAuth2Validator()
        self.endpoint = Server(validator)

    def get_uri(self):
        base_uri = self.request.protocol + '://' + self.request.host
        uri = base_uri + self.request.uri
        return base_uri, uri

    def get_method(self):
        return self.request.method

    def get_body(self):
        return self.request.body

    def get_headers(self):
        return self.request.headers

    def get_client_ip(self):
        return self.request.remote_ip

    def get_current_user(self):
        return self.get_secure_cookie('user')

    def write_error(self, status_code, **kwargs):
        self.set_status(status_code, self._reason)
        result = {
            'message': self._reason,
            'status': status_code,
        }
        self.write(result)

    def raise400(self, reason=None, log_message=None):
        self.abort(400, reason, log_message)

    def raise401(self, reason=None, log_message=None):
        self.abort(401, reason, log_message)

    def raise403(self, reason=None, log_message=None):
        self.abort(403, reason, log_message)

    def raise404(self, reason=None, log_message=None):
        self.abort(404, reason, log_message)

    def abort(self, status, reason=None, log_message=None):
        raise tornado.web.HTTPError(
            status, reason=reason, log_message=log_message)

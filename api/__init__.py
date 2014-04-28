#!/usr/bin/env python
#
# @name: __init__.py
# @date: Apr. 22th, 2014
# @author: hitigon@gmail.com
import tornado.web

RESP_MSG = {
    1000: 'create successfully',
    1001: 'update successfully',
    1002: 'delete successfully',
    1003: 'login successfully',
    -1000: 'create failed',
    -1001: 'update failed',
    -1002: 'delete failed',
    -1003: 'login failed',
    -1004: 'incomplete fields',
}


def get_respmsg(code):
    if code in RESP_MSG:
        return {code: RESP_MSG[code]}
    else:
        return {0: 'unknown'}


class BaseHandler(tornado.web.RequestHandler):

    def get_current_user(self):
        return self.get_secure_cookie('user')

    def raise401(self, reason=None, log_message=None):
        raise tornado.web.HTTPError(401, reason, log_message)

    def raise403(self, reason=None, log_message=None):
        raise tornado.web.HTTPError(403, reason, log_message)

    def raise404(self, reason=None, log_message=None):
        raise tornado.web.HTTPError(404, reason, log_message)

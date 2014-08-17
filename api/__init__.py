#!/usr/bin/env python
#
# @name: api/__init__.py
# @create: Apr. 22th, 2014
# @update: Aug. 14th, 2014
# @author: hitigon@gmail.com
import tornado.web
from mongoengine.connection import get_db
from oauthlib.oauth2 import Server
from oauth.validator import OAuth2Validator


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

ERROR_CODE = {
    'ValidationError': -1000,
    'NotUniqueError': -1001,
    'DoesNotExist': -1002,
    'OperationError': -1003,
    'ValueError': -1004,
    'AttributeError': -1005,
    'KeyError': -1006,
    'InvalidRequestError': -1006,
    'MissingClientIdError': -1006,
    'InvalidQueryError': -1007,
    'LookUpError': -1008,
    'TypeError': -1008,
}

SUCCESS_CODE = {
    'QuerySuccess': 1000,
    'CreateSuccess': 1001,
    'UpdateSuccess': 1002,
    'DeleteSuccess': 1003,
    'AuthSuccess': 1004,
    'TokenSuccess': 1005,
}


class Success(object):

    def __init__(self, msg):
        self.message = msg


class QuerySuccess(Success):
    pass


class UpdateSuccess(Success):
    pass


class DeleteSuccess(Success):
    pass


class CreateSuccess(Success):
    pass


class AuthSuccess(Success):
    pass


class TokenSuccess(Success):
    pass


def get_respmsg(code, data=None):
    if code in RESP_MSG:
        return {'code': code, 'msg': RESP_MSG[code], 'data': data}
    else:
        return {'code': 0, 'msg': 'unknown'}


def get_error_code(error_type):
    global ERROR_CODE
    return ERROR_CODE[error_type]


def get_success_code(success_type):
    global SUCCESS_CODE
    return SUCCESS_CODE[success_type]


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

    def get_response(self, code=None, msgs=None, data=None, error=None,
                     success=None):
        response = {
            'code': code or 0,
            'messages': msgs,
            'data': data,
        }
        if error and not code and not msgs:
            code = get_error_code(str(type(error).__name__))
            msgs = []
            if hasattr(error, 'errors'):
                for k, v in error.errors.items():
                    msgs.append(str(v) + '(' + str(k) + ')')
            else:
                msgs.append(error.message or error.error)
            response['code'] = code
            response['messages'] = msgs
        if success and not code:
            code = get_success_code(str(type(success).__name__))
            response['code'] = code
            response['messages'] = msgs or success.message
        return response

    def raise401(self, reason=None, log_message=None):
        raise tornado.web.HTTPError(401, reason, log_message)

    def raise403(self, reason=None, log_message=None):
        raise tornado.web.HTTPError(403, reason, log_message)

    def raise404(self, reason=None, log_message=None):
        raise tornado.web.HTTPError(404, reason, log_message)

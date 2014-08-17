#!/usr/bin/env python
#
# @name: api/auth.py
# @create: Aug. 10th, 2014
# @update: Aug. 14th, 2014
# @author: hitigon@gmail.com
import json
from urlparse import urlparse, parse_qs
from tornado.escape import url_escape
from bson import ObjectId
from mongoengine.errors import ValidationError
from . import BaseHandler, AuthSuccess, TokenSuccess
from libs.utils import request_to_binary, binary_to_request
from models.user import User
from models.oauth.client import Client
from models.oauth.credential import Credential


class AuthHandler(BaseHandler):

    def get(self, *args):
        base_uri, uri = self.get_uri()
        response = {}
        try:
            scopes, credentials = self.endpoint.validate_authorization_request(
                uri, 'GET', {}, {})
            # Be careful, client_id and user_id are not verified in this step
            client_id = credentials['client_id']
            user_id = parse_qs(urlparse(uri).query)['user_id'][0]
            state = credentials['state']
            redirect_uri = base_uri + credentials['redirect_uri']
            request = request_to_binary(credentials['request'])
            response_type = credentials['response_type']
            Credential(
                client_id=client_id, user_id=user_id, state=state,
                redirect_uri=redirect_uri, request=request,
                response_type=response_type).save()
            msg = 'Authorization request validated'
            response = self.get_response(
                data={'scopes': scopes}, success=AuthSuccess(msg))
        except Exception as e:
            response = self.get_response(error=e)
        self.write(response)

    def post(self, *args):
        if args:
            self.raise403()
        client_id = self.get_argument('client_id', None)
        user_id = self.get_argument('user_id', None)
        scopes = self.get_argument('scopes', [])
        base_uri, uri = self.get_uri()

        try:
            if scopes:
                scopes = [s.strip()
                          for s in scopes.split(' ') if len(s.strip()) > 0]
            #print(scopes)
            client = Client.objects(client_id=client_id).first()
            user = User.objects(id=ObjectId(user_id)).first()
            cred = Credential.objects(
                client_id=client_id, user_id=user_id).first()
            if not client or not user or not cred:
                raise ValidationError('Authorization failed')
            credentials = {
                'client_id': cred.client_id,
                'response_type': cred.response_type,
                'request': binary_to_request(cred.request),
                'redirect_uri': cred.redirect_uri,
                'state': cred.state,
                'user': user,
            }
            content = self.endpoint.create_authorization_response(
                uri, 'GET', {}, {}, scopes, credentials)
            self.redirect(content[0]['Location'])
        except Exception as e:
            self.write(self.get_response(error=e))

'''
class CodeHandler(BaseHandler):

    def get(self, *args):
        base_uri, uri = self.get_uri()
        query = parse_qs(urlparse(uri).query)
        if 'code' in query:
            data = {'code': query['code'][0]}
            msg = 'Authorization code returned'
            self.write(
                self.get_response(data=data, success=AuthSuccess(msg)))
        else:
            self.raise401()
'''


class TokenHandler(BaseHandler):

    def post(self, *args):
        if args:
            self.raise403()
        grant_type = self.get_argument('grant_type', None)
        code = self.get_argument('code', None)
        redirect_uri = self.get_argument('redirect_uri', None)
        client_id = self.get_argument('client_id', None)
        scope = self.get_argument('scope', None)
        username = self.get_argument('username', None)
        password = self.get_argument('password', None)

        base_uri, uri = self.get_uri()
        error_msg = 'Token request failed'
        response = {}
        try:
            if not grant_type:
                raise ValidationError(error_msg)
            body = ''
            headers = {'Authorization': 'Basic ksjdhf923sf'}
            if grant_type == 'authorization_code':
                if not code:
                    raise ValidationError(error_msg)
                body += 'grant_type=authorization_code&'
                body += 'code=%s&' % code
                body += 'redirect_uri=%s&' % url_escape(redirect_uri)
                body += 'client_id=%s&' % client_id
                print(body)
            elif grant_type == 'password':
                if not password or not username:
                    raise ValidationError(error_msg)
                body += 'grant_type=password&'
                body += 'client_id=%s&' % client_id
                body += 'username=%s&password=%s&' % (username, password)
                body += 'scope=%s&' % scope if len(scope) > 0 else ''
            elif grant_type == 'client_credentials':
                body += 'grant_type=client_credentials&'
                body += 'scope=%s&' % scope
            else:
                raise ValidationError(error_msg)
            headers, body, status = self.endpoint.create_token_response(
                base_uri + '/token', 'POST', body, headers, {})
            # error messages should be handlered here
            # body['error'], body['error_description']

            # password login behaviors
            msg = 'Token returned'
            data = json.loads(body)
            data['username'] = username
            response = self.get_response(data=data, success=TokenSuccess(msg))
        except Exception as e:
            response = self.get_response(error=e)
        self.write(response)

#!/usr/bin/env python
#
# @name: api/auth.py
# @create: Aug. 10th, 2014
# @update: Aug. 22th, 2014
# @author: hitigon@gmail.com
import json
from urlparse import urlparse, parse_qs
from tornado.escape import url_escape
from bson import ObjectId
from utils import parse_listed_strs
from utils import request_to_binary, binary_to_request
from base import BaseHandler
from models.user import User
from models.oauth.client import Client
from models.oauth.credential import Credential
from models.oauth.token import Token


class AuthHandler(BaseHandler):

    def get(self, *args, **kwargs):
        try:
            base_uri, uri = self.get_uri()
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
            data = {'scopes': scopes}
            self.write(data)
        except Exception as e:
            reason = e.message
            self.raise400(reason=reason)

    def post(self, *args, **kwargs):
        client_id = self.get_argument('client_id', None)
        user_id = self.get_argument('user_id', None)
        scopes = self.get_argument('scopes', [])

        try:
            base_uri, uri = self.get_uri()
            scopes_list = parse_listed_strs(scopes)
            client = Client.objects(client_id=client_id).first()
            user = User.objects(id=ObjectId(user_id)).first()
            cred = Credential.objects(
                client_id=client_id, user_id=user_id).first()
            if not client or not user or not cred:
                raise Exception('Authorization failed')
            credentials = {
                'client_id': cred.client_id,
                'response_type': cred.response_type,
                'request': binary_to_request(cred.request),
                'redirect_uri': cred.redirect_uri,
                'state': cred.state,
                'user': user,
            }
            content = self.endpoint.create_authorization_response(
                uri, 'GET', {}, {}, scopes_list, credentials)
            self.redirect(content[0]['Location'])
        except Exception as e:
            self.write(self.get_response(error=e))


class TokenHandler(BaseHandler):

    def post(self, *args, **kwargs):
        grant_type = self.get_argument('grant_type', None)
        code = self.get_argument('code', None)
        redirect_uri = self.get_argument('redirect_uri', None)
        client_id = self.get_argument('client_id', None)
        scope = self.get_argument('scope', None)
        username = self.get_argument('username', None)
        password = self.get_argument('password', None)
        refresh_token = self.get_argument('refresh_token', None)

        try:
            msg = 'Token request failed: %s'
            if not grant_type:
                raise Exception(msg % 'missing grant_type')
            body = ''
            base_uri, uri = self.get_uri()
            headers = self.get_headers()
            if grant_type == 'authorization_code':
                if not code:
                    raise Exception(msg % 'missing code')
                body += 'grant_type=authorization_code&'
                body += 'code=%s&' % code
                body += 'redirect_uri=%s&' % url_escape(redirect_uri)
                body += 'client_id=%s&' % client_id
            elif grant_type == 'password':
                if not password or not username:
                    raise Exception(msg % 'missing password or username')
                body += 'grant_type=password&'
                body += 'client_id=%s&' % client_id
                body += 'username=%s&password=%s&' % (username, password)
                body += 'scope=%s&' % scope if len(scope) > 0 else ''
            elif grant_type == 'client_credentials':
                body += 'grant_type=client_credentials&'
                body += 'scope=%s&' % scope
            elif grant_type == 'refresh_token':
                body += 'grant_type=refresh_token&'
                body += 'refresh_token=%s&' % refresh_token
                body += 'client_id=%s&' % client_id
            else:
                raise Exception(msg % 'unknown grant_type')
            headers, body, status = self.endpoint.create_token_response(
                base_uri + '/token', 'POST', body, headers, {})
            # error messages should be handlered here
            # body['error'], body['error_description']

            # password login behaviors
            data = json.loads(body)
            token = Token.objects(access_token=data['access_token']).first()
            user = token.user
            data['username'] = user.username
            self.set_status(201)
            self.write(data)
        except Exception as e:
            reason = e.message
            self.raise400(reason=reason)

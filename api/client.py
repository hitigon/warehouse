#!/usr/bin/env python
#
# @name: api/client.py
# @create: Aug. 10th, 2014
# @update: Aug. 21th, 2014
# @author: hitigon@gmail.com
from __future__ import print_function
import re
import json
from mongoengine.errors import DoesNotExist
from utils import create_id, create_secret
from base import BaseHandler
from models.user import User
from models.oauth.client import Client

__all__ = ('Client',)


class ClientHandler(BaseHandler):

    '''temp handler just for testing
    '''
    def get(self, *args, **kwargs):
        response = {}
        # client = Client.objects
        # data = json.loads(client.to_json())
        # msg = 'Found clients'
        # response = self.get_response(data=data, success=QuerySuccess(msg))
        self.write(response)

    def post(self, *args, **kwargs):
        #print(decode_basic_auth(self.request.headers['Authorization']))

        # username = self.get_argument('username', None)
        # grant_type = self.get_argument('grant_type', None)
        # response_type = self.get_argument('response_type', None)
        # redirect_uris = self.get_argument('redirect_uris', None)
        # app_name = self.get_argument('app_name', None)
        # description = self.get_argument('description', None)
        # response = {}
        # try:
        #     user = User.objects(username=username).first()
        #     if not user:
        #         raise DoesNotExist('User does not exist')
        #     client_id = create_id()
        #     client_secret = create_secret()
        #     grant_type = grant_type or 'authorization_code'
        #     response_type = response_type or 'code'
        #     default_scopes = ['tasks', 'projects', 'repos', 'users', 'teams']
        #     scopes = default_scopes
        #     redirect_uris, default_redirect_uri = process_uris(redirect_uris)

        #     client = Client(
        #         client_id=client_id, client_secret=client_secret,
        #         user=user, grant_type=grant_type,
        #         response_type=response_type, scopes=scopes,
        #         default_scopes=default_scopes, redirect_uris=redirect_uris,
        #         default_redirect_uri=default_redirect_uri,
        #         app_name=app_name, description=description)
        #     client.save()
        #     client_data = json.loads(client.to_json())
        #     msg = 'Client Added'
        #     response = self.get_response(
        #         data=client_data, success=CreateSuccess(msg))
        # except Exception as e:
        #     response = self.get_response(error=e)
        response = {}
        self.write(response)

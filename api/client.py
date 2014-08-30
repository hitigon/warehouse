#!/usr/bin/env python
#
# @name: api/client.py
# @create: Aug. 10th, 2014
# @update: Aug. 29th, 2014
# @author: hitigon@gmail.com
from __future__ import print_function
from utils import parse_path, parse_listed_strs
from utils import document_to_json, query_to_json
from utils import create_id, create_secret
from base import BaseHandler
from oauth.protector import authenticated
from models.oauth.client import Client

__all__ = ('Client',)

_FILTER = {
    'user': {
        'password': False,
        'ip': False,
        'create_time': False,
        'login_time': False,
    },
}


class ClientHandler(BaseHandler):

    @authenticated(scopes=["users"])
    def get(self, *args, **kwargs):
        # /clients
        # /clients/:app_name
        if 'user' not in kwargs:
            self.raise401()
        user = kwargs['user']

        if args:
            path = parse_path(args[0])
            client = Client.objects(user=user, app_name=path[0]).first()
            if not client:
                self.raise404()
            client_data = document_to_json(client, filter_set=_FILTER)
        else:
            limit = self.get_argument('limit', None)
            start = self.get_argument('start', None)
            try:
                limit = int(limit)
            except:
                limit = None
            try:
                start = int(start)
            except:
                start = None
            clients = Client.objects(user=user)
            if limit and start:
                clients = clients[start: start+limit]
            elif limit:
                clients = clients[:limit]
            elif start:
                clients = clients[start:]
            client_data = query_to_json(clients, filter_set=_FILTER)
        self.write(client_data)

    @authenticated(scopes=["users"])
    def post(self, *args, **kwargs):
        if 'user' not in kwargs or args:
            self.raise401()

        grant_type = self.get_argument('grant_type', None)
        response_type = self.get_argument('response_type', None)
        redirect_uris = self.get_argument('redirect_uris', None)
        app_name = self.get_argument('app_name', None)
        description = self.get_argument('description', None)
        website = self.get_argument('website', None)

        try:
            user = kwargs['user']
            client_id = create_id()
            client_secret = create_secret()
            grant_type = grant_type or 'authorization_code'
            response_type = response_type or 'code'
            # todo scopes
            default_scopes = ['tasks', 'projects', 'repos', 'users', 'teams']
            scopes = default_scopes
            redirect_uris = parse_listed_strs(redirect_uris)
            # todo default
            default_redirect_uri = redirect_uris[0] if redirect_uris else ''

            client = Client(
                client_id=client_id, client_secret=client_secret,
                user=user, grant_type=grant_type,
                response_type=response_type, scopes=scopes,
                default_scopes=default_scopes, redirect_uris=redirect_uris,
                default_redirect_uri=default_redirect_uri, website=website,
                app_name=app_name, description=description)
            client.save()
            client_data = document_to_json(client, filter_set=_FILTER)
            self.set_status(201)
            self.write(client_data)
        except Exception as e:
            reason = e.message
            self.raise400(reason=reason)

    @authenticated(scopes=["users"])
    def put(self, *args, **kwargs):
        if 'user' not in kwargs or not args:
            self.raise401()

        # redirect_uris = self.get_argument('redirect_uris', None)
        app_name = self.get_argument('app_name', None)
        description = self.get_argument('description', None)
        website = self.get_argument('website', None)
        update = {}
        if app_name:
            update['set__app_name'] = app_name
        if description:
            update['set__description'] = description
        if website:
            update['set__website'] = website
        # if redirect_uris:
        #     update['set_redirect_uris'] = parse_listed_strs(redirect_uris)
        user = kwargs['user']
        path = parse_path(args[0])
        client = Client.objects(app_name=path[0]).first()
        if not client or user != client.user:
            self.raise401()
        try:
            Client.objects(app_name=path[0]).update_one(**update)
            client = Client.objects(app_name=app_name or path[0]).first()
            client_data = document_to_json(client, filter_set=_FILTER)
            self.set_status(201)
            self.write(client_data)
        except Exception as e:
            reason = e.message
            self.raise400(reason=reason)

    @authenticated(scopes=["users"])
    def delete(self, *args, **kwargs):
        if 'user' not in kwargs or not args:
            self.raise401()
        user = kwargs['user']
        path = parse_path(args[0])
        client = Client.objects(app_name=path[0]).first()
        if not client or user != client.user:
            self.raise401()
        try:
            Client.objects(app_name=path[0]).delete()
            self.set_status(204)
            self.finish()
        except Exception as e:
            reason = e.message
            self.raise400(reason=reason)

#!/usr/bin/env python
#
# @name: api/user.py
# @create: Apr. 27th, 2014
# @update: Aug. 27th, 2014
# @author: hitigon@gmail.com
from __future__ import print_function
from utils import parse_path, create_password
from utils import document_to_json
from base import BaseHandler
from oauth.protector import authenticated
from models.user import User

_FILTER = {
    'password': False,
    'ip': False,
    'create_time': False,
    'login_time': False,
}


class ProfileHandler(BaseHandler):

    @authenticated(scopes=['users'])
    def get(self, *args, **kwargs):
        # need project/team information
        if 'user' not in kwargs:
            self.raise401()

        user = kwargs['user']
        if args:
            path = parse_path(args[0])
            if user.username != path[0]:
                user = User.objects(username=path[0]).first()
        self.write(document_to_json(user, filter_set=_FILTER))

    @authenticated(scopes=['users'])
    def put(self, *args, **kwargs):
        if args or 'user' not in kwargs:
            self.raise401()

        username = self.get_argument('username', None)
        email = self.get_argument('email', None)
        password = self.get_argument('password', None)
        first_name = self.get_argument('first_name', None)
        last_name = self.get_argument('last_name', None)

        user = kwargs['user']
        update = {}
        if username:
            update['set__username'] = username
        if email:
            update['set__email'] = email
        if password:
            update['set__password'] = create_password(password)
        if first_name:
            update['set__first_name'] = first_name
        if last_name:
            update['set__last_name'] = last_name

        try:
            User.objects(username=user.username).update_one(**update)
            user = User.objects(name=username or user.username).first()
            self.set_status(201)
            self.write(document_to_json(user, filter_set=_FILTER))
        except Exception as e:
            reason = e.message
            self.raise400(reason=reason)

    @authenticated(scopes=['users'])
    def delete(self, *args, **kwargs):
        # auth code and token
        if args or 'user' not in kwargs:
            self.raise401()
        user = kwargs['user']
        try:
            User.objects(username=user.username).delete()
            self.set_status(204)
            self.finish()
        except Exception as e:
            reason = e.message
            self.raise400(reason=reason)


class RegisterHandler(BaseHandler):

    def post(self, *args, **kwargs):
        username = self.get_argument('username', None)
        email = self.get_argument('email', None)
        password = self.get_argument('password', None)
        first_name = self.get_argument('first_name', None)
        last_name = self.get_argument('last_name', None)
        ip = self.get_argument('user_ip', None)

        try:
            password = create_password(password) if password else None
            user = User(username=username, email=email,
                        password=password, first_name=first_name,
                        last_name=last_name, ip=ip).save()
            self.set_status(201)
            self.write(document_to_json(user, filter_set=_FILTER))
        except Exception as e:
            reason = e.message
            self.raise400(reason=reason)

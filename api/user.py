#!/usr/bin/env python
#
# @name: api/user.py
# @create: Apr. 27th, 2014
# @update: Aug. 21th, 2014
# @author: hitigon@gmail.com
from __future__ import print_function
from . import BaseHandler
from libs.utils import parse_path, create_password
from libs.utils import document_only_filter
from models.user import User
from oauth.protector import authenticated


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
        filter_set = set(
            ['id', 'username', 'email', 'first_name', 'last_name'])
        self.write(document_only_filter(user, filter_set))

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
            filter_set = set(
                ['id', 'username', 'email', 'first_name', 'last_name'])
            self.set_status(201)
            self.write(document_only_filter(user, filter_set))
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
            filter_set = set(
                ['id', 'username', 'email', 'first_name', 'last_name'])
            self.set_status(201)
            self.write(document_only_filter(user, filter_set))
        except Exception as e:
            reason = e.message
            self.raise400(reason=reason)

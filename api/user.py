#!/usr/bin/env python
#
# @name: api/user.py
# @date: Apr. 27th, 2014
# @author: hitigon@gmail.com
from __future__ import print_function
import bcrypt
import tornado.web
from bson import ObjectId
from model import user
from . import BaseHandler
from . import get_respmsg


class LoginHandler(BaseHandler):

    def post(self):
        account = self.get_argument('account', None)
        password = self.get_argument('password', None)

        if account and password:
            spec = {'$or': [{'username': account}, {'email': account}]}
            result = user.query(spec)

            if result:
                hashedpw = result['password'].encode()
                if hashedpw == bcrypt.hashpw(password.encode(), hashedpw):
                    self.set_secure_cookie('user', result['_id'])
                    response = get_respmsg(1003)
            else:
                response = get_respmsg(-1003)
        else:
            response = get_respmsg(-1003)
        self.write(response)


class UserHandler(BaseHandler):

    @tornado.web.authenticated
    def get(self, query_id=None):
        if query_id:
            if ObjectId.is_valid(query_id):
                response = user.query(query_id)
            else:
                spec = {'username': query_id}
                response = user.query(spec)
        else:
            response = user.query_all()

        if response is None:
            response = {}
        self.write(response)

    def post(self):
        username = self.get_argument('username', None)
        email = self.get_argument('email', None)
        password = self.get_argument('password', None)
        first_name = self.get_argument('first_name', None)
        last_name = self.get_argument('last_name', None)
        group = self.get_argument('group', 1)

        if username and email and password:
            password = bcrypt.hashpw(password.encode(), bcrypt.gensalt())
            name = {
                'first': first_name,
                'last': last_name,
            }
            result = user.create(username, email, password, name, group)
            if result:
                response = get_respmsg(1000)
            else:
                response = get_respmsg(-1000)
        else:
            response = get_respmsg(-1004)

        self.write(response)

    def put(self, query_id):
        username = self.get_argument('username', None)
        email = self.get_argument('email', None)
        password = self.get_argument('password', None)
        first_name = self.get_argument('first_name', None)
        last_name = self.get_argument('last_name', None)
        group = self.get_argument('group', None)

        update = {}
        if username:
            update['username'] = username
        if email:
            update['email'] = email
        # need old password!
        if password:
            update['password'] = bcrypt.hashpw(password, bcrypt.gensalt())
        if first_name or last_name:
            update['name']['first'] = first_name
            update['name']['last'] = last_name
        # group
        if group:
            update['group'] = int(group)
        document = {'$set': update}
        if user.update(query_id, document):
            response = get_respmsg(1001)
        else:
            response = get_respmsg(-1001)

        self.write(response)

    def delete(self, query_id):
        if ObjectId.is_valid(query_id):
            spec = query_id
        else:
            spec = {'username': query_id}
        if user.delete(spec):
            response = get_respmsg(1002)
        else:
            response = get_respmsg(-1002)
        self.write(response)

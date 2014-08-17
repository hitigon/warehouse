#!/usr/bin/env python
#
# @name: api/user.py
# @create: Apr. 27th, 2014
# @update: Aug. 14th, 2014
# @author: hitigon@gmail.com
from __future__ import print_function
import json
import bcrypt
#from bson import ObjectId
from mongoengine.errors import DoesNotExist, OperationError
from models.user import User
from oauth.protector import authenticated
from . import BaseHandler, DeleteSuccess
from . import QuerySuccess, CreateSuccess, UpdateSuccess


class UserHandler(BaseHandler):

    @authenticated(scopes=['users'])
    def get(self, *args, **kwargs):
        response = {}
        users = None
        query = None

        if args:
            if len(args) == 1:
                query = args[0]
            else:
                self.raise404()
        if query:
            users = User.objects(username=query).first()
        else:
            users = User.objects.all()

        if users:
            msg = 'Found User'
            users = json.loads(users.to_json())
            response = self.get_response(data=users, success=QuerySuccess(msg))
        else:
            msg = 'User does not exists'
            response = self.get_response(error=DoesNotExist(msg))
        self.write(response)

    def post(self, *args, **kwargs):
        if args:
            n = len(args)
            if n == 1 or (n == 2 and args[1] == 'edit'):
                return self.put(*args)
            elif n == 2 and args[1] == 'delete':
                return self.delete(*args)
            else:
                self.raise404()
        create_user(self)

    @authenticated(scopes=['users'])
    def put(self, *args):
        if not args:
            self.raise403()
        if len(args) >= 2:
            if args[1] == 'delete':
                return self.delete(*args)
            elif args[1] != 'edit':
                self.raise404()
        response = {}
        update = {}

        username = self.get_argument('username', None)
        email = self.get_argument('email', None)
        password = self.get_argument('password', None)
        first_name = self.get_argument('first_name', None)
        last_name = self.get_argument('last_name', None)

        if username:
            update['set__username'] = username
        if email:
            update['set__email'] = email
        if password:
            update['set__password'] = bcrypt.hashpw(password, bcrypt.gensalt())
        if first_name:
            update['set__first_name'] = first_name
        if last_name:
            update['set__last_name'] = last_name

        try:
            query = args[0]
            user = User.objects(username=query)
            if user.count() == 0:
                raise DoesNotExist('User does not exist')
            result = user.update_one(**update)
            if result == 0:
                raise OperationError('Update failed')
            msg = 'User Updated'
            response = self.get_response(success=UpdateSuccess(msg))
        except Exception as e:
            response = self.get_response(error=e)
        self.write(response)

    @authenticated(scopes=['users'])
    def delete(self, *args, **kwargs):
        if not args:
            self.raise403()
        if len(args) >= 2:
            if args[1] == 'edit':
                return self.put(*args)
            elif args[1] != 'delete':
                self.raise404()
        response = {}
        try:
            query = args[0]
            user = User.objects(username=query)
            if user.count() == 0:
                raise DoesNotExist('User does not exist')
            user.delete()
            if User.objects(username=query).count() != 0:
                raise OperationError('Deletion failed')
            msg = 'User Deleted'
            response = self.get_response(success=DeleteSuccess(msg))
        except Exception as e:
            response = self.get_response(error=e)
        self.write(response)


class SignupHandler(BaseHandler):

    def post(self, *args, **kwargs):
        if args:
            self.raise403()
        create_user(self, 'Signed up')
        '''
        username = self.get_argument('username', None)
        email = self.get_argument('email', None)
        password = self.get_argument('password', None)
        first_name = self.get_argument('first_name', None)
        last_name = self.get_argument('last_name', None)
        '''
        # print(self.auth_endpoint)

'''
class SigninHandler(BaseHandler):

    def post(self, *args):
        if args:
            self.raise403()
        username = self.get_argument('username', None)
        password = self.get_argument('password', None)
        print(username, password)
        response = {}

        self.write(response)
'''


def create_user(obj, success_msg=None):
    username = obj.get_argument('username', None)
    email = obj.get_argument('email', None)
    password = obj.get_argument('password', None)
    first_name = obj.get_argument('first_name', None)
    last_name = obj.get_argument('last_name', None)

    response = {}
    if password:
        password = bcrypt.hashpw(password.encode(), bcrypt.gensalt())

    try:
        user = User(username=username, email=email,
                    password=password, first_name=first_name,
                    last_name=last_name, ip=obj.get_client_ip())
        user.save()
        user_data = json.loads(user.to_json())
        response = obj.get_response(
            data=user_data, success=CreateSuccess(success_msg or 'User added'))
    except Exception as e:
        response = obj.get_response(error=e)

    obj.write(response)

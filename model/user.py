#!/usr/bin/env python
#
# @name: model/user.py
# @date: Apr. 27th, 2014
# @author: hitigon@gmail.com
from __future__ import print_function
from pymongo import errors
from bson import ObjectId
from model import db
from lib import util

user = db.user


def create(username, email, password, name, group):
    spec = {
        'username': username,
        'email': email,
        'password': password,
        'name': name,
        'group': group,
        'create_time': util.get_utc_timestamp(),
    }
    try:
        user_id = user.insert(spec)
        return user_id
    except errors.OperationFailure as e:
        print(e)
    return False


def query(spec_or_id):
    if spec_or_id is None:
        return None
    try:
        if ObjectId.is_valid(spec_or_id):
            result = user.find_one(ObjectId(spec_or_id))
        else:
            result = user.find_one(spec_or_id)
        result['_id'] = str(result['_id'])
        return result
    except TypeError as e:
        print(e)
    return result


def query_all():
    try:
        items = user.find()
        if items:
            result = {}
            for item in items:
                item['_id'] = str(item['_id'])
                result[item['username']] = item
            return result
    except TypeError as e:
        print(e)
    return None


def update(name_or_id, document):
    if name_or_id is None or document is None:
        return False
    try:
        if ObjectId.is_valid(name_or_id):
            spec = {'_id': ObjectId(name_or_id)}
        else:
            spec = {'username': name_or_id}
        user.update(spec, document)
        return True
    except errors.OperationFailure as e:
        print(e)
    except TypeError as e:
        print(e)
    return False


def delete(spec_or_id):
    if spec_or_id is None:
        return False
    try:
        if ObjectId.is_valid(spec_or_id):
            user.remove(ObjectId(spec_or_id))
        else:
            user.remove(spec_or_id)
        return True
    except errors.OperationFailure as e:
        print(e)
    return False


def delete_all():
    try:
        user.remove()
        return True
    except errors.OperationFailure as e:
        print(e)
    return False


def create_indexes():
    username = user.ensure_index('username', unique=True)
    email = user.ensure_index('email', unique=True)
    uuid = user.ensure_index('uuid', unique=True)
    if username and email and uuid:
        return True
    return False

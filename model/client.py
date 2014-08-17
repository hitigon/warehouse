#!/usr/bin/env python
#
# @name: model/client.py
# @date: Jun. 9th, 2014
# @author: hitigon@gmail.com
from __future__ import print_function
from pymongo import errors
from bson import ObjectId
from model import db

client = db.client


def create(user, grant, response, scopes, uris):
    spec = {
        'user': user,
        #'authorization_code', 'Authorization code'
        'grant': grant,
        #'code', 'Authorization code'
        'response': response,
        'scopes': scopes,
        'default_scopes': [],
        'uris': uris,
        'default_uris': [],
    }
    try:
        client_id = client.insert(spec)
        return client_id
    except errors.OperationFailure as e:
        print(e)
    return False


def query(spec_or_id):
    if spec_or_id is None:
        return None
    try:
        if ObjectId.is_valid(spec_or_id):
            result = client.find_one(ObjectId(spec_or_id))
        else:
            result = client.find_one(spec_or_id)
        result['_id'] = str(result['_id'])
        return result
    except TypeError as e:
        print(e)
    return result

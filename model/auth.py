#!/usr/bin/env python
#
# @name: model/auth.py
# @date: Apr. 27th, 2014
# @author: hitigon@gmail.com
from __future__ import print_function
from pymongo import errors
#from bson import ObjectId
from model import db

auth = db.auth


def create(client, user, scopes, code, expires):
    spec = {
        'client': client,
        'user': user,
        'scopes': scopes,
        'code': code,  # unique
        'expires': expires,
    }
    try:
        auth_id = auth.insert(spec)
        return auth_id
    except errors.OperationFailure as e:
        print(e)
    return False


def create_indexes():
    code = auth.ensure_index('code', unique=True)
    return code is not None

#!/usr/bin/env python
#
# @name: model/token.py
# @date: Jun. 9th, 2014
# @author: hitigon@gmail.com
from __future__ import print_function
from pymongo import errors
#from bson import ObjectId
from model import db

token = db.token


def create(client, user, scopes, access, refresh, expires):
    spec = {
        'client': client,
        'user': user,
        'scopes': scopes,
        'access': access,
        'refresh': refresh,
        'expires': expires,
    }
    try:
        token_id = token.insert(spec)
        return token_id
    except errors.OperationFailure as e:
        print(e)
    return False


def create_indexes():
    access = token.ensure_index('access', unique=True)
    refresh = token.ensure_index('refresh', unique=True)

    if access and refresh:
        return True
    else:
        return False

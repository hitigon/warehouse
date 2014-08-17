#!/usr/bin/env python
#
# @name: model/__init__.py
# @date: Apr. 22th, 2014
# @author: hitigon@gmail.com

from __future__ import print_function
from pymongo import MongoClient
from pymongo import errors
from config import DB_DATABASE, DB_HOST, DB_PORT


__all__ = ['db', 'client']

'''
def connect(host, port):
    client = None
    try:
        client = MongoClient(host, port)
    except errors.ConnectionFailure as e:
        print(e)
    return client


def get_db(client, database):
    db = None
    if client is not None:
        try:
            db = client[database]
        except ValueError as e:
            print(e)
    return db


def disconnect(client):
    client.disconnect()

client = connect(DB_HOST, DB_PORT)

if client:
    db = get_db(client, DB_DATABASE)
'''

db = None
client = None

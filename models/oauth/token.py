#!/usr/bin/env python
#
# @name: models/oauth/token.py
# @create: Aug. 9th, 2014
# @update: Aug. 9th, 2014
# @author: hitigon@gmail.com
from __future__ import print_function
from mongoengine import Document
from mongoengine import StringField, ListField
from mongoengine import ReferenceField, DateTimeField

__all__ = ('Token',)


class Token(Document):
    from client import Client
    from ..user import User
    client = ReferenceField(Client)
    user = ReferenceField(User)
    scopes = ListField(StringField())
    access_token = StringField(max_length=100, unique=True)
    refresh_token = StringField(max_length=100, unique=True)
    expires_at = DateTimeField()

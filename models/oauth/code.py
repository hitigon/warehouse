#!/usr/bin/env python
#
# @name: models/oauth/code.py
# @create: Aug. 9th, 2014
# @update: Aug. 9th, 2014
# @author: hitigon@gmail.com
from __future__ import print_function
from mongoengine import Document
from mongoengine import StringField, ListField
from mongoengine import ReferenceField, DateTimeField

__all__ = ('Code',)


class Code(Document):
    from client import Client
    from ..user import User
    client = ReferenceField(Client)
    user = ReferenceField(User)
    scopes = ListField(StringField())
    code = StringField(max_length=100, unique=True)
    redirect_uri = StringField()
    state = StringField()
    expires_at = DateTimeField()

#!/usr/bin/env python
#
# @name: models/user.py
# @create: Aug. 7th, 2014
# @update: Aug. 21th, 2014
# @author: hitigon@gmail.com
from __future__ import print_function
from datetime import datetime
from mongoengine import Document
from mongoengine import StringField, DateTimeField
from mongoengine import EmailField

__all__ = ('User',)


class User(Document):
    username = StringField(required=True, unique=True)
    email = EmailField(required=True, unique=True)
    password = StringField(required=True)
    first_name = StringField()
    last_name = StringField()
    ip = StringField()
    create_time = DateTimeField(default=datetime.utcnow())
    login_time = DateTimeField()

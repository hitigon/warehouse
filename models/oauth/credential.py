#!/usr/bin/env python
#
# @name: models/oauth/token.py
# @create: Aug. 11th, 2014
# @update: Aug. 11th, 2014
# @author: hitigon@gmail.com
from __future__ import print_function
from mongoengine import Document
from mongoengine import StringField, BinaryField

__all__ = ('Credential',)


class Credential(Document):
    client_id = StringField()
    user_id = StringField()
    response_type = response_type = StringField(
        max_length=5, choices=['code', 'token'])
    request = BinaryField()
    redirect_uri = StringField()
    state = StringField()

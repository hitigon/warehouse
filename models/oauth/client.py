#!/usr/bin/env python
#
# @name: models/oauth/client.py
# @create: Aug. 9th, 2014
# @update: Aug. 9th, 2014
# @author: hitigon@gmail.com
from __future__ import print_function
from mongoengine import Document
from mongoengine import StringField, ListField, DateTimeField
from mongoengine import ReferenceField, URLField
from libs.utils import get_utc_time

__all__ = ('Client',)


class Client(Document):
    from ..user import User
    client_id = StringField(unique=True)
    client_secret = StringField()
    user = ReferenceField(User)
    grant_type = StringField(max_length=18, choices=[
                             'authorization_code', 'implicit',
                             'client_credentials', 'password'])
    response_type = StringField(
        max_length=5, choices=['code', 'token'])
    scopes = ListField(StringField())
    default_scopes = ListField(StringField())
    redirect_uris = ListField(URLField())
    default_redirect_uri = URLField()
    app_name = StringField()
    website = URLField()
    description = StringField()
    create_time = DateTimeField(default=get_utc_time())

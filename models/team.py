#!/usr/bin/env python
#
# @name: models/team.py
# @create: Aug. 8th, 2014
# @update: Aug. 21th, 2014
# @author: hitigon@gmail.com
from __future__ import print_function
from mongoengine import Document
from mongoengine import StringField, DateTimeField, URLField
from mongoengine import ListField, ReferenceField
from utils import get_utc_time


__all__ = ('Team',)


class Team(Document):
    from user import User
    name = StringField(required=True, unique=True)
    description = StringField()
    url = URLField()
    leader = ReferenceField(User)
    members = ListField(ReferenceField(User))
    create_time = DateTimeField(default=get_utc_time())
    tags = ListField(StringField())

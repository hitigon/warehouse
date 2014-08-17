#!/usr/bin/env python
#
# @name: models/team.py
# @date: Aug. 8th, 2014
# @author: hitigon@gmail.com
from __future__ import print_function
from datetime import datetime
from mongoengine import Document
from mongoengine import StringField, DateTimeField, URLField
from mongoengine import ListField, ReferenceField


__all__ = ('Team',)


class Team(Document):
    name = StringField(required=True, unique=True)
    description = StringField()
    url = URLField()
    from user import User
    founder = ReferenceField(User)
    members = ListField(ReferenceField(User))
    create_time = DateTimeField(default=datetime.utcnow())
    update_time = DateTimeField()
    tags = ListField(StringField())

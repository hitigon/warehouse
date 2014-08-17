#!/usr/bin/env python
#
# @name: models/project.py
# @create: Aug. 8th, 2014
# @update: Aug. 8th, 2014
# @author: hitigon@gmail.com
from __future__ import print_function
from datetime import datetime
from mongoengine import Document
from mongoengine import StringField, DateTimeField, URLField
from mongoengine import IntField, ListField, ReferenceField
from user import User
from team import Team
from repo import Repo

__all__ = ('Project',)


class Project(Document):
    name = StringField(required=True, unique=True)
    description = StringField()
    url = URLField()
    status = IntField(default=0)
    repos = ListField(ReferenceField(Repo))
    leader = ReferenceField(User)
    members = ListField(ReferenceField(User))
    teams = ListField(ReferenceField(Team))
    create_time = DateTimeField(default=datetime.utcnow())
    update_time = DateTimeField()
    tags = ListField(StringField())

#!/usr/bin/env python
#
# @name: models/repo.py
# @create: Aug. 8th, 2014
# @update: Aug. 21th, 2014
# @author: hitigon@gmail.com
from __future__ import print_function
from datetime import datetime
from mongoengine import Document
from mongoengine import StringField, DateTimeField
from mongoengine import IntField, ListField, ReferenceField

__all__ = ('Repo',)


class Repo(Document):
    from user import User
    from team import Team
    name = StringField(required=True, unique=True)
    description = StringField()
    path = StringField()
    scm = StringField(
        default='Git', choices=['Git', 'Mercurial', 'SVN', 'CVS'])
    status = IntField(default=0)
    owner = ReferenceField(User)
    team = ReferenceField(Team)
    create_time = DateTimeField(default=datetime.utcnow())
    update_time = DateTimeField()
    tags = ListField(StringField())

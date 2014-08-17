#!/usr/bin/env python
#
# @name: models/comment.py
# @date: Aug. 8th, 2014
# @author: hitigon@gmail.com
from __future__ import print_function
from datetime import datetime
from mongoengine import EmbeddedDocument
from mongoengine import StringField, DateTimeField
from mongoengine import ReferenceField


__all__ = ('ProjectComment', 'TaskComment', 'RepoComment')


class ProjectComment(EmbeddedDocument):
    content = StringField()
    from user import User
    user = ReferenceField(User)
    create_time = DateTimeField(default=datetime.utcnow())
    update_time = DateTimeField()


class TaskComment(EmbeddedDocument):
    content = StringField()
    from user import User
    user = ReferenceField(User)
    create_time = DateTimeField(default=datetime.utcnow())
    update_time = DateTimeField()


class RepoComment(EmbeddedDocument):
    content = StringField()
    from user import User
    user = ReferenceField(User)
    create_time = DateTimeField(default=datetime.utcnow())
    update_time = DateTimeField()
    # commit
    # file/code

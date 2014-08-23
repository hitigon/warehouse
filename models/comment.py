#!/usr/bin/env python
#
# @name: models/comment.py
# @create: Aug. 8th, 2014
# @update: Aug. 23th, 2014
# @author: hitigon@gmail.com
from __future__ import print_function
from mongoengine import EmbeddedDocument
from mongoengine import StringField, DateTimeField
from mongoengine import ReferenceField, BooleanField
from utils import get_utc_time

__all__ = ('ProjectComment', 'TaskComment', 'CodeComment')


class ProjectComment(EmbeddedDocument):
    content = StringField(required=True)
    from user import User
    author = ReferenceField(User)
    reply_to = ReferenceField(User)
    create_time = DateTimeField(default=get_utc_time())


class TaskComment(EmbeddedDocument):
    from user import User
    content = StringField(required=True)
    author = ReferenceField(User)
    create_time = DateTimeField(default=get_utc_time())


class CodeComment(EmbeddedDocument):
    from user import User
    lines = StringField(required=True)
    content = StringField(required=True)
    author = ReferenceField(User)
    create_time = DateTimeField(default=get_utc_time())


class CodeReview(EmbeddedDocument):
    content = StringField(required=True)
    from user import User
    reviewer = ReferenceField(User)
    approved = BooleanField(default=False)
    create_time = DateTimeField(default=get_utc_time())

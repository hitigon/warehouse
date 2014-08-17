#!/usr/bin/env python
#
# @name: models/task.py
# @date: Aug. 8th, 2014
# @author: hitigon@gmail.com
from __future__ import print_function
from datetime import datetime
from mongoengine import Document
from mongoengine import StringField, DateTimeField, EmbeddedDocumentField
from mongoengine import IntField, ListField, ReferenceField


__all__ = ('Task',)


class Task(Document):
    description = StringField(required=True)
    category = IntField(default=0)  # 0:new
    from user import User
    from project import Project
    from comment import TaskComment
    project = ReferenceField(Project)
    status = IntField(default=0)
    priority = IntField(default=0)
    members = ListField(ReferenceField(User))
    due = DateTimeField()
    create_time = DateTimeField(default=datetime.utcnow())
    update_time = DateTimeField()
    tags = ListField(StringField())
    comments = ListField(EmbeddedDocumentField(TaskComment))

#!/usr/bin/env python
#
# @name: models/task.py
# @create: Aug. 8th, 2014
# @update: Aug. 21th, 2014
# @author: hitigon@gmail.com
from __future__ import print_function
from mongoengine import Document
from mongoengine import StringField, DateTimeField, EmbeddedDocumentField
from mongoengine import ListField, ReferenceField
from utils import get_utc_time

__all__ = ('Task',)


class Task(Document):
    description = StringField(required=True)
    category = StringField(required=True)
    from user import User
    from project import Project
    from comment import TaskComment
    project = ReferenceField(Project)
    status = StringField(default='new', choices=[
                         'new', 'in progress', 'testing',
                         'complete', 'closed'])
    priority = StringField(
        default='normal', choices=['low', 'normal', 'high', 'emergency'])
    assign_to = ListField(ReferenceField(User))
    due = DateTimeField()
    create_time = DateTimeField(default=get_utc_time())
    update_time = DateTimeField()
    tags = ListField(StringField())
    comments = ListField(EmbeddedDocumentField(TaskComment))

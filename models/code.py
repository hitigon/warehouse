#!/usr/bin/env python
#
# @name: models/code.py
# @create: Aug. 21th, 2014
# @update: Aug. 21th, 2014
# @author: hitigon@gmail.com
from __future__ import print_function
from mongoengine import Document
from mongoengine import StringField, DateTimeField, EmbeddedDocumentField
from mongoengine import ListField, ReferenceField, BooleanField


__all__ = ('Code',)


class Code(Document):
    from user import User
    from task import Task
    from repo import Repo
    from comment import CodeComment
    from comment import CodeReview
    task = ReferenceField(Task)
    repo = ReferenceField(Repo)
    description = StringField()
    file_name = StringField()
    author = ReferenceField(User)
    reviewers = ListField(ReferenceField(User))
    approved = BooleanField(default=False)
    create_time = DateTimeField()
    tags = ListField(StringField())
    reviews = ListField(EmbeddedDocumentField(CodeReview))
    comments = ListField(EmbeddedDocumentField(CodeComment))

#!/usr/bin/env python
#
# @name: model/project.py
# @date: Apr. 26th, 2014
# @author: hitigon@gmail.com
from __future__ import print_function
from pymongo import errors
from model import db

project = db.project


def create(name, tags=None):
    spec = {
        'name': name,
        'desp': '',
        'status': 0,
        'leader': '',
        'members': [],
        'repos': [],
        'tags': tags,
        'create_time': 0,
    }
    try:
        project_id = project.insert(spec)
        return project_id
    except errors.OperationFailure as e:
        print(e)
    return False


def query(spec_or_id):
    pass


def update():
    pass


def delete():
    pass

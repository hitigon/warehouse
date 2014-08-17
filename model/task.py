#!/usr/bin/env python
#
# @name: model/task.py
# @date: June 10th, 2014
# @author: hitigon@gmail.com
from __future__ import print_function
from pymongo import errors
from bson import ObjectId
from model import db
from lib import util

task = db.task


def create(
    category, description, project, due_time, status=None,
        priority=None, members=None, tags=None):
    spec = {
        'category': category,
        'description': description,
        'project': project,
        'status': 0,
        'priority': 0,
        'members': members,
        'tags': tags,
        'create_time': util.get_utc_timestamp(),
        'update_time': None,
        'due_time': due_time,
    }
    try:
        task_id = task.insert(spec)
        return task_id
    except errors.OperationFailure as e:
        print(e)
    return False


def query(spec_or_id):
    if spec_or_id is None:
        return None
    try:
        if ObjectId.is_valid(spec_or_id):
            result = task.find_one(ObjectId(spec_or_id))
        else:
            result = task.find_one(spec_or_id)
        result['_id'] = str(result['_id'])
        return result
    except TypeError as e:
        print(e)
    return result


def query_all():
    try:
        items = task.find()
        if items:
            result = {}
            for item in items:
                item['_id'] = str(item['_id'])
                result[item['_id']] = item
            return result
    except TypeError as e:
        print(e)
    return None


def update(query_id, document):
    if query_id is None or document is None:
        return False
    try:
        if ObjectId.is_valid(query_id):
            spec = {'_id': ObjectId(query_id)}
            task.update(spec, document)
            return True
    except errors.OperationFailure as e:
        print(e)
    except TypeError as e:
        print(e)
    return False


def delete(spec_or_id):
    if spec_or_id is None:
        return False
    try:
        if ObjectId.is_valid(spec_or_id):
            task.remove(ObjectId(spec_or_id))
        else:
            task.remove(spec_or_id)
        return True
    except errors.OperationFailure as e:
        print(e)
    return False


def delete_all():
    try:
        task.remove()
        return True
    except errors.OperationFailure as e:
        print(e)
    return False

#!/usr/bin/env python
#
# @name: model/project.py
# @date: Apr. 26th, 2014
# @author: hitigon@gmail.com
from __future__ import print_function
from pymongo import errors
from bson import ObjectId
from model import db
from model import repo
from model import user
from lib import util

project = db.project


def create(name, description=None, leader=None, members=None, repos=None,
           tags=None):
    spec = {
        'name': name,
        'description': description,
        'status': 0,
        'leader': leader,
        'members': members,
        'repos': repos,
        'tags': tags,
        'create_time': util.get_utc_timestamp(),
    }
    try:
        project_id = project.insert(spec)
        return project_id
    except errors.OperationFailure as e:
        print(e)
    return False


def query(spec_or_id):
    if spec_or_id is None:
        return None
    try:
        if ObjectId.is_valid(spec_or_id):
            result = project.find_one(ObjectId(spec_or_id))
        else:
            result = project.find_one(spec_or_id)
        result['_id'] = str(result['_id'])
        if result['repos']:
            repos = {}
            for r in result['repos']:
                repos[str(r)] = repo.query(r)
            result['repos'] = repos
        return result
    except TypeError as e:
        print(e)
    return result


def query_all():
    try:
        items = project.find()
        if items:
            result = {}
            for item in items:
                item['_id'] = str(item['_id'])
                if item['leader']:
                    item['leader'] = user.query(item['leader'])
                if item['members']:
                    members = {}
                    for m in item['members']:
                        members[str(m)] = user.query(m)
                    item['members'] = members
                if item['repos']:
                    repos = {}
                    for r in item['repos']:
                        repos[str(r)] = repo.query(r)
                    item['repos'] = repos
                result[item['_id']] = item
            return result
    except TypeError as e:
        print(e)
    return None


def update(name_or_id, document):
    if name_or_id is None or document is None:
        return False
    try:
        if ObjectId.is_valid(name_or_id):
            spec = {'_id': ObjectId(name_or_id)}
        else:
            spec = {'name': name_or_id}
        project.update(spec, document)
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
            project.remove(ObjectId(spec_or_id))
        else:
            project.remove(spec_or_id)
        return True
    except errors.OperationFailure as e:
        print(e)
    return False


def delete_all():
    try:
        project.remove()
        return True
    except errors.OperationFailure as e:
        print(e)
    return False

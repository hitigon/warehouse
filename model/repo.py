#!/usr/bin/env python
#
# @name: model/repo.py
# @date: Apr. 22th, 2014
# @author: hitigon@gmail.com
from __future__ import print_function
from pymongo import errors
from bson import ObjectId
from model import db

repo = db.repo


def create(name, path, scm='git', project=None, tags=None):
    project = (project is not None and ObjectId.is_valid(
        project)) and ObjectId(project) or None
    spec = {
        'name': name,
        'path': path,
        'scm': scm,
        'project': project,
        'tags': tags
    }
    try:
        repo_id = repo.insert(spec)
        return repo_id
    except errors.OperationFailure as e:
        print(e)
    return False


def query(spec_or_id):
    if spec_or_id is None:
        return None
    try:
        if ObjectId.is_valid(spec_or_id):
            result = repo.find_one(ObjectId(spec_or_id))
        else:
            result = repo.find_one(spec_or_id)
        result['_id'] = str(result['_id'])
        project = result['project']
        if project is not None:
            result['project'] = str(project)
        return result
    except TypeError as e:
        print(e)
    return result


def query_all():
    try:
        items = repo.find()
        if items:
            result = {}
            for item in items:
                item['_id'] = str(item['_id'])
                project = item['project']
                if project is not None:
                    item['project'] = str(project)
                result[item['name']] = item
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
        repo.update(spec, document)
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
            repo.remove(ObjectId(spec_or_id))
        else:
            repo.remove(spec_or_id)
        return True
    except errors.OperationFailure as e:
        print(e)
    return False


def delete_all():
    try:
        repo.remove()
        return True
    except errors.OperationFailure as e:
        print(e)
    return False


def create_indexes():
    name = repo.ensure_index('name', unique=True)
    return name is not None

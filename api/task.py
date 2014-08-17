#!/usr/bin/env python
#
# @name: api/project.py
# @date: June. 10th, 2014
# @author: hitigon@gmail.com
from __future__ import print_function
import tornado.web
from bson import ObjectId
from model import task
from . import get_respmsg


class TaskHandler(tornado.web.RequestHandler):

    def get(self, query_id=None):
        if query_id:
            if ObjectId.is_valid(query_id):
                response = task.query(query_id)
            else:
                spec = {'category': query_id}
                response = task.query(spec)
        else:
            response = task.query_all()

        if not response:
            response = {}
        self.write(response)

    def post(self):
        category = self.get_argument('category', None)
        description = self.get_argument('description', None)
        project = self.get_argument('project', None)
        status = self.get_argument('priority', 0)
        priority = self.get_argument('priority', 0)
        members = self.get_argument('members', None)
        due_time = self.get_argument('due_time', None)
        tags = self.get_argument('tags', None)

        if not category or not description or not project:
            response = get_respmsg(-1004)
        else:
            result = task.create(
                category, description, project, due_time,
                status, priority, members, tags)
            if result:
                data = task.query(result)
                response = get_respmsg(1000, data)
            else:
                response = get_respmsg(-1000)
        self.write(response)

    def put(self, query_id):
        category = self.get_argument('category', None)
        description = self.get_argument('description', None)
        project = self.get_argument('project', None)
        status = self.get_argument('priority', 0)
        priority = self.get_argument('priority', 0)
        members = self.get_argument('members', None)
        due_time = self.get_argument('due_time', None)
        tags = self.get_argument('tags', None)

        update = {}
        if category:
            update['category'] = category
        if description:
            update['description'] = description
        if project:
            update['project'] = project
        if members:
            update['members'] = members
        if status:
            update['status'] = status
        if priority:
            update['priority'] = priority
        if due_time:
            update['due_time'] = due_time
        if tags:
            update['tags'] = [str(tag).strip() for tag in tags.split(',')]
        document = {'$set': update}
        if task.update(query_id, document):
            data = task.query(query_id)
            response = get_respmsg(1001, data)
        else:
            response = get_respmsg(-1001)

        self.write(response)

    def delete(self, query_id):
        if ObjectId.is_valid(query_id):
            spec = query_id
        if task.delete(spec):
            response = get_respmsg(1002)
        else:
            response = get_respmsg(-1002)
        self.write(response)

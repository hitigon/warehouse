#!/usr/bin/env python
#
# @name: api/project.py
# @create: Jun. 10th, 2014
# @update: Aug. 21th, 2014
# @author: hitigon@gmail.com
from __future__ import print_function
from base import BaseHandler
from oauth.protector import authenticated
from models.task import Task


class TaskHandler(BaseHandler):

    @authenticated(scopes=['tasks'])
    def get(self, *args, **kwargs):
        # /task
        # /task/:id
        # if query_id:
        #     if ObjectId.is_valid(query_id):
        #         response = task.query(query_id)
        #     else:
        #         spec = {'category': query_id}
        #         response = task.query(spec)
        # else:
        #     response = task.query_all()

        # if not response:
        response = {}
        self.write(response)

    @authenticated(scopes=['tasks'])
    def post(self, *args, **kwargs):
        # category = self.get_argument('category', None)
        # description = self.get_argument('description', None)
        # project = self.get_argument('project', None)
        # status = self.get_argument('priority', 0)
        # priority = self.get_argument('priority', 0)
        # members = self.get_argument('members', None)
        # due_time = self.get_argument('due_time', None)
        # tags = self.get_argument('tags', None)

        # if not category or not description or not project:
        #     response = get_respmsg(-1004)
        # else:
        #     result = task.create(
        #         category, description, project, due_time,
        #         status, priority, members, tags)
        #     if result:
        #         data = task.query(result)
        #         response = get_respmsg(1000, data)
        #     else:
        #         response = get_respmsg(-1000)
        response = {}
        self.write(response)

    @authenticated(scopes=['tasks'])
    def put(self, *args, **kwargs):
        # category = self.get_argument('category', None)
        # description = self.get_argument('description', None)
        # project = self.get_argument('project', None)
        # status = self.get_argument('priority', 0)
        # priority = self.get_argument('priority', 0)
        # members = self.get_argument('members', None)
        # due_time = self.get_argument('due_time', None)
        # tags = self.get_argument('tags', None)

        # update = {}
        # if category:
        #     update['category'] = category
        # if description:
        #     update['description'] = description
        # if project:
        #     update['project'] = project
        # if members:
        #     update['members'] = members
        # if status:
        #     update['status'] = status
        # if priority:
        #     update['priority'] = priority
        # if due_time:
        #     update['due_time'] = due_time
        # if tags:
        #     update['tags'] = [str(tag).strip() for tag in tags.split(',')]
        # document = {'$set': update}
        # if task.update(query_id, document):
        #     data = task.query(query_id)
        #     response = get_respmsg(1001, data)
        # else:
        #     response = get_respmsg(-1001)
        response = {}
        self.write(response)

    @authenticated(scopes=['tasks'])
    def delete(self, *args, **kwargs):
        # if ObjectId.is_valid(query_id):
        #     spec = query_id
        # if task.delete(spec):
        #     response = get_respmsg(1002)
        # else:
        #     response = get_respmsg(-1002)
        response = {}
        self.write(response)

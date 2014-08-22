#!/usr/bin/env python
#
# @name: api/project.py
# @create: Jun. 10th, 2014
# @update: Aug. 22th, 2014
# @author: hitigon@gmail.com
from __future__ import print_function
from utils import get_utc_time
from utils import parse_path, parse_listed_strs
from utils import document_to_json, query_to_json
from base import BaseHandler
from oauth.protector import authenticated
from models.task import Task
from models.project import Project
from models.user import User

_SUB_FILTER = {
    'password': False,
    'ip': False,
    'create_time': False,
    'login_time': False,
}

_FILTER = {
    'project': {
        'leader': _SUB_FILTER,
        'members': _SUB_FILTER,
        'repos': {
            'owner': _SUB_FILTER,
            'team': {
                'leader': _SUB_FILTER,
                'members': _SUB_FILTER,
            },
        },
    },
    'assign_to': _SUB_FILTER,
}


class TaskHandler(BaseHandler):

    @authenticated(scopes=['tasks'])
    def get(self, *args, **kwargs):
        # 1, all tasks in your projects
        # 2, all user's tasks
        # 3, specified task (id)
        # /tasks
        # /tasks/:id
        # /tasks/?project=
        # /tasks/?username=
        if 'user' not in kwargs:
            self.raise401()

        user = kwargs['user']

        if args:
            path = parse_path(args[0])
            task = Task.objects(id=path[0]).first()
            if not task:
                self.raise404()
            task_data = document_to_json(task, filter_set=_FILTER)
        else:
            username = self.get_argument('username', None)
            project_name = self.get_argument('project', None)
            try:
                project_name = parse_path(project_name)[0]
            except IndexError:
                project_name = None
            try:
                username = parse_path(username)[0]
            except IndexError:
                username = None
            if project_name and username:
                user = User.objects(username=username).first()
                project = Project.objects(name=project_name).first()
                tasks = Task.objects(
                    project=project, assign_to__in=[user]).all()
            elif project_name:
                project = Project.objects(name=project_name).first()
                tasks = Task.objects(project=project).all()
            elif username:
                user = User.objects(username=username).first()
                tasks = Task.objects(assign_to__in=[user]).all()
            else:
                projects = Project.objects(members__in=[user]).all()
                tasks = []
                for project in projects:
                    ts = Task.objects(project=project).all()
                    tasks += list(ts)
            task_data = query_to_json(tasks, filter_set=_FILTER)
        self.write(task_data)

    @authenticated(scopes=['tasks'])
    def post(self, *args, **kwargs):
        if 'user' not in kwargs or args:
            self.raise401()
        category = self.get_argument('category', None)
        description = self.get_argument('description', None)
        project_name = self.get_argument('project', None)
        status = self.get_argument('status', None)
        priority = self.get_argument('priority', None)
        assign_to = self.get_argument('assign_to', None)
        due = self.get_argument('due', None)  # days or date
        tags = self.get_argument('tags', None)
        user = kwargs['user']
        project = Project.objects(name=project_name).first()
        if not project or user not in project.members:
            self.raise401()
        try:
            due_day = int(due)
        except ValueError:
            due_day = 0

        try:
            assign_to_list = []
            if assign_to:
                for member in parse_listed_strs(assign_to):
                    u = User.objects(username=member).first()
                    if not u:
                        continue
                    assign_to_list.append(u)
            due_time = get_utc_time(due_day * 24 * 3600)
            tags_list = parse_listed_strs(tags)
            task = Task(
                category=category, description=description, project=project,
                status=status, priority=priority, assign_to=assign_to_list,
                due=due_time, tags=tags_list)
            task.save()
            task_data = document_to_json(task, filter_set=_FILTER)
            self.set_status(201)
            self.write(task_data)
        except Exception as e:
            reason = e.message
            self.raise400(reason=reason)

    @authenticated(scopes=['tasks'])
    def put(self, *args, **kwargs):
        if 'user' not in kwargs or not args:
            self.raise401()
        update = {}
        user = kwargs['user']
        task_id = parse_path(args[0])[0]
        task = Task.objects(id=task_id).first()
        project = task.project
        if not project or user not in project.members:
            self.raise401()
        category = self.get_argument('category', None)
        description = self.get_argument('description', None)
        project_name = self.get_argument('project', None)
        status = self.get_argument('status', None)
        priority = self.get_argument('priority', None)
        assign_to = self.get_argument('assign_to', None)
        due = self.get_argument('due', None)
        tags = self.get_argument('tags', None)

        if category:
            update['set__category'] = category
        if description:
            update['set__description'] = description
        if project_name:
            project = Project.objects(name=project_name).first()
            if not project or user not in project.members:
                self.raise401()
            update['set__project'] = project
        if assign_to:
            assign_to_list = []
            for member in parse_listed_strs(assign_to):
                u = User.objects(username=member).first()
                if not u:
                    continue
                assign_to_list.append(u)
            update['set__assign_to'] = assign_to_list
        if status:
            update['set__status'] = status
        if priority:
            update['set__priority'] = priority
        if due:
            try:
                due_day = int(due)
            except ValueError:
                due_day = 0
            due_time = get_utc_time(due_day * 24 * 3600)
            update['set__due'] = due_time
        if tags:
            tags_list = parse_listed_strs(tags)
            update['set__tags'] = tags_list
        try:
            Task.objects(id=task_id).update_one(**update)
            task = Task.objects(id=task_id).first()
            task_data = document_to_json(task, filter_set=_FILTER)
            self.set_status(201)
            self.write(task_data)
        except Exception as e:
            reason = e.message
            self.raise400(reason=reason)

    @authenticated(scopes=['tasks'])
    def delete(self, *args, **kwargs):
        if 'user' not in kwargs or not args:
            self.raise401()
        user = kwargs['user']
        task_id = parse_path(args[0])[0]
        task = Task.objects(id=task_id).first()
        project = task.project
        if not project or user not in project.members:
            self.raise401()
        try:
            Task.objects(id=task_id).delete()
            self.set_status(204)
            self.finish()
        except Exception as e:
            reason = e.message
            self.raise400(reason=reason)

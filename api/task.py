#!/usr/bin/env python
#
# @name: api/project.py
# @create: Jun. 10th, 2014
# @update: Aug. 21th, 2014
# @author: hitigon@gmail.com
from __future__ import print_function
from utils import get_utc_time
from utils import parse_path, parse_listed_strs
from utils import convert_query, convert_document
from base import BaseHandler
from oauth.protector import authenticated
from models.task import Task
from models.project import Project
from models.user import User


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
            task_data = convert_document(task)
        else:
            project_name = self.get_argument('project', None)
            username = self.get_argument('username', None)
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
                    task = Task.objects(project=project).first()
                    tasks.append(task)
            task_data = convert_query(tasks)
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
        assign_to = self.get_argument('members', None)
        due = self.get_argument('due', None)  # days or date
        tags = self.get_argument('tags', None)

        try:
            due_day = int(due)
        except ValueError:
            due_day = 0

        try:
            user = kwargs['user']
            project = Project.objects(name=project_name).first()
            if not project or user not in project.members:
                raise Exception('unauthenticated project')
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
            self.set_status(201)
            self.write(convert_document(task))
        except Exception as e:
            reason = e.message
            self.raise400(reason=reason)

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

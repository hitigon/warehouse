#!/usr/bin/env python
#
# @name: api/project.py
# @create: Apr. 25th, 2014
# @update: Aug. 14th, 2014
# @author: hitigon@gmail.com
from __future__ import print_function
import json
from mongoengine.errors import DoesNotExist
from . import BaseHandler
from . import QuerySuccess
from models.project import Project
from models.user import User
from models.team import Team


class ProjectHandler(BaseHandler):

    def get(self, *args):
        response = {}
        projects = None

        if args:
            n = len(args)
            if n == 1:
                projects = Project.objects(name=args[0]).all()
            elif n == 2:
                if args[0] == 'user':
                    user = User.objects(username=args[1]).first()
                    projects = Project.objects(members__in=[user]).all()
                elif args[0] == 'team':
                    team = Team.objects(name=args[1]).first()
                    projects = Project.objects(teams__in=[team]).all()
            else:
                self.raise404()
        else:
            projects = Project.objects.all()

        if projects:
            msg = 'Found projects'
            projects = json.loads(projects.to_json())
            response = self.get_response(
                data=projects, success=QuerySuccess(msg))
        else:
            msg = 'Project does not exists'
            response = self.get_response(error=DoesNotExist(msg))
        self.write(response)

    def post(self, *args):
        '''
        name = self.get_argument('name', None)
        description = self.get_argument('description', None)
        leader = self.get_argument('leader', None)
        members = self.get_argument('members', None)
        repos = self.get_argument('repos', None)
        tags = self.get_argument('tags', None)
        if not name:
            response = get_respmsg(-1004)
        else:

            if repos:
                valid_repos = []
                tmp = repos.split(',')
                for t in tmp:
                    t = t.strip()
                    if repo.query(t):
                        valid_repos.append(ObjectId(t))
                if len(valid_repos) > 0:
                    repos = valid_repos
            if members:
                valid_members = []
                tmp = repos.split(',')
                for t in tmp:
                    t = t.strip()
                    if user.query(t):
                        valid_repos.append(ObjectId(t))
                if len(valid_members) > 0:
                    members = valid_members
            result = project.create(
                name, description, leader, members, repos, tags)
            if result:
                data = project.query(result)
                response = get_respmsg(1000, data)
            else:
                response = get_respmsg(-1000)
        '''
        response = {}
        self.write(response)

    def put(self, *args):
        '''

        name = self.get_argument('name', None)
        description = self.get_argument('description', None)
        leader = self.get_argument('leader', None)
        members = self.get_argument('members', None)
        repos = self.get_argument('repos', None)
        tags = self.get_argument('tags', None)
        response = {}
        update = {}
        if name:
            update['name'] = name
        if description:
            update['description'] = description
        if leader:
            update['leader'] = leader
        if members:
            update['members'] = members
        if repos:
            update['repos'] = repos
        if tags:
            update['tags'] = [str(tag).strip() for tag in tags.split(',')]
        document = {'$set': update}
        if project.update(query_id, document):
            data = project.query(query_id)
            response = get_respmsg(1001, data)
        else:
            response = get_respmsg(-1001)
        '''
        response = {}
        self.write(response)

    def delete(self, *args):
        response = {}
        '''
        if ObjectId.is_valid(query_id):
            spec = query_id
        else:
            spec = {'name': query_id}
        if project.delete(spec):
            response = get_respmsg(1002)
        else:
            response = get_respmsg(-1002)
        '''
        self.write(response)

#!/usr/bin/env python
#
# @name: api/project.py
# @create: Apr. 25th, 2014
# @update: Aug. 19th, 2014
# @author: hitigon@gmail.com
from __future__ import print_function
import json
from mongoengine.errors import DoesNotExist
from . import BaseHandler
from . import QuerySuccess
from libs.utils import parse_listed_strs
from models.project import Project
from models.user import User
from models.team import Team
from models.repo import Repo
from oauth.protector import authenticated


class ProjectHandler(BaseHandler):

    @authenticated(scopes=['projects'])
    def get(self, *args, **kwags):
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

    @authenticated(scopes=['projects'])
    def post(self, *args, **kwargs):
        name = self.get_argument('name', None)
        description = self.get_argument('description', None)
        url = self.get_argument('url', None)
        leader = self.get_argument('leader', None)
        members = self.get_argument('members', None)
        teams = self.get_argument('teams', None)
        repos = self.get_argument('repos', None)
        tags = self.get_argument('tags', None)
        if 'user' not in kwargs:
            self.raise401()

        try:
            project_leader = kwargs['user']
            if leader:
                project_leader = User.objects(username=leader).first()
            members_list = []
            repos_list = []
            teams_list = []
            tags_list = parse_listed_strs(tags)
            for repo in parse_listed_strs(repos):
                r = Repo.objects(name=repo).first()
                repos_list.append(r)
            for member in parse_listed_strs(members):
                u = User.objects(username=member).first()
                members_list.append(u)
            for team in parse_listed_strs(teams):
                t = Team.objects(name=team).first()
                teams_list.append(t)
            project = Project(
                name=name, description=description,
                url=url, repos=repos_list,
                leader=project_leader, members=members_list,
                teams=teams_list, tags=tags_list)
            project.save()
            project_data = json.loads(project.to_json())
            self.set_status(201)
            self.write(project_data)
        except Exception as e:
            reason = e.message
            self.raise400(reason=reason)

    def put(self, *args, **kwargs):
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

    def delete(self, *args, **kwargs):
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

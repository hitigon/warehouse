#!/usr/bin/env python
#
# @name: api/project.py
# @create: Apr. 25th, 2014
# @update: Aug. 22th, 2014
# @author: hitigon@gmail.com
from __future__ import print_function
from oauth.protector import authenticated
from base import BaseHandler
from utils import parse_listed_strs, parse_path
from utils import document_to_json, query_to_json
from models.project import Project
from models.user import User
from models.team import Team
from models.repo import Repo

_SUB_FILTER = {
    'password': False,
    'ip': False,
    'create_time': False,
    'login_time': False,
}

_FILTER = {
    'leader': _SUB_FILTER,
    'members': _SUB_FILTER,
    'team': {
        'leader': _SUB_FILTER,
        'members': _SUB_FILTER,
    },
    'repos': {
        'owner': _SUB_FILTER,
        'team': {
            'leader': _SUB_FILTER,
            'members': _SUB_FILTER,
        }
    },
}


class ProjectHandler(BaseHandler):

    @authenticated(scopes=['projects'])
    def get(self, *args, **kwargs):
        # /projects/
        # /projects/:name (+)
        # /projects/?username= (*)
        # /projects/?team= (*)
        if 'user' not in kwargs:
            self.raise401()

        user = kwargs['user']
        if args:
            path = parse_path(args[0])
            project = Project.objects(name=path[0]).first()
            if not project:
                self.raise404()
            if project and user not in project.members:
                self.raise401()
            project_data = document_to_json(project, filter_set=_FILTER)
        else:
            project = Project.objects(members__in=[user]).all()
            project_data = query_to_json(project, filter_set=_FILTER)
        self.write(project_data)

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
            # todo - better arguments handler
            url = url.strip()
            url = url if url else None
            members_list = []
            repos_list = []
            teams_list = []
            project_leader = kwargs['user']
            if leader:
                project_leader = User.objects(username=leader).first()

            if repos:
                for repo in parse_listed_strs(repos):
                    r = Repo.objects(name=repo).first()
                    if not r:
                        continue
                    repos_list.append(r)
            if members:
                for member in parse_listed_strs(members):
                    u = User.objects(username=member).first()
                    if not u or u == project_leader:
                        continue
                    members_list.append(u)
            if teams:
                for team in parse_listed_strs(teams):
                    t = Team.objects(name=team).first()
                    if not t:
                        continue
                    teams_list.append(t)
            members_list.append(project_leader)
            tags_list = parse_listed_strs(tags)
            project = Project(
                name=name, description=description,
                url=url, repos=repos_list,
                leader=project_leader, members=members_list,
                teams=teams_list, tags=tags_list)
            project.save()
            project_data = document_to_json(project, filter_set=_FILTER)
            self.set_status(201)
            self.write(project_data)
        except Exception as e:
            reason = e.message
            self.raise400(reason=reason)

    @authenticated(scopes=['projects'])
    def put(self, *args, **kwargs):
        # the creator of the project might be neither
        # the leader nor the member
        # it causes a problem that the creator cannot
        # access, modify and delete the project
        if 'user' not in kwargs or not args:
            self.raise401()
        name = self.get_argument('name', None)
        description = self.get_argument('description', None)
        url = self.get_argument('url', None)
        leader = self.get_argument('leader', None)
        members = self.get_argument('members', None)
        teams = self.get_argument('teams', None)
        repos = self.get_argument('repos', None)
        tags = self.get_argument('tags', None)

        user = kwargs['user']
        path = parse_path(args[0])
        project = Project.objects(name=path[0]).first()
        if not project or user not in project.members:
            self.raise401()
        project_leader = project.leader
        update = {}
        if name:
            update['set__name'] = name
        if description:
            update['set__description'] = description
        if url:
            update['set__url'] = url
        if leader:
            project_leader = User.objects(username=leader).first()
            update['set__leader'] = project_leader
        if members:
            members_list = []
            for member in parse_listed_strs(members):
                u = User.objects(username=member).first()
                if not u or u == project_leader:
                    continue
                members_list.append(u)
            members_list.append(project_leader)
            update['set__members'] = members_list
        if teams:
            teams_list = []
            for team in parse_listed_strs(teams):
                t = Team.objects(name=team).first()
                if not t:
                    continue
                teams_list.append(t)
            update['set__teams'] = teams_list
        if repos:
            repos_list = []
            for repo in parse_listed_strs(repos):
                r = Repo.objects(name=repo).first()
                if not r:
                    continue
                repos_list.append(r)
            update['set__repos'] = repos_list
        if tags:
            tags_list = parse_listed_strs(tags)
            update['set__tags'] = tags_list
        try:
            Project.objects(name=path[0]).update_one(**update)
            project = Repo.objects(name=name or path[0]).first()
            project_data = document_to_json(project, filter_set=_FILTER)
            self.set_status(201)
            self.write(project_data)
        except Exception as e:
            reason = e.message
            self.raise400(reason=reason)

    @authenticated(scopes=['projects'])
    def delete(self, *args, **kwargs):
        if 'user' not in kwargs or not args:
            self.raise401()

        user = kwargs['user']
        path = parse_path(args[0])
        project = Project.objects(name=path[0], members__in=[user])
        if not project:
            self.raise401()
        try:
            project.delete()
            self.set_status(204)
            self.finish()
        except Exception as e:
            reason = e.message
            self.raise400(reason=reason)

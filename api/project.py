#!/usr/bin/env python
#
# @name: api/project.py
# @create: Apr. 25th, 2014
# @update: Aug. 20th, 2014
# @author: hitigon@gmail.com
from __future__ import print_function
import json
from oauth.protector import authenticated
from . import BaseHandler
from libs.utils import parse_listed_strs, parse_path
from models.project import Project
from models.user import User
from models.team import Team
from models.repo import Repo


class ProjectHandler(BaseHandler):

    @authenticated(scopes=['projects'])
    def get(self, *args, **kwargs):
        if 'user' not in kwargs:
            self.raise401()

        user = kwargs['user']
        if args:
            path = parse_path(args[0])
            project = Project.objects(name=path[0]).first()
            if project and user not in project.members:
                self.raise401()
        else:
            project = Project.objects(members__in=[user]).all()
        if project:
            project_data = json.loads(project.to_json())
            self.write(json.dumps(project_data))
        else:
            self.raise404()

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
            print(project)
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

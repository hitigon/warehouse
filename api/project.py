# -*- coding: utf-8 -*-
#!/usr/bin/env python
#
# @name: api/project.py
# @create: Apr. 25th, 2014
# @update: Aug. 30th, 2014
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

__all__ = ('ProjectHandler',)


class ProjectHandler(BaseHandler):

    @authenticated(scopes=['projects'])
    def get(self, *args, **kwargs):
        """Retrieve the resources of projects for the current user.

        If `*args` is provided by matching the URL pattern, the first element
        in the args is considered as a project name, then the project data will
        be retrieved from Database and send back to the client and the source
        owner in the format of JSON.
        Otherwise, it responses with a list of projects parcipated by the
        user. The request can provide three arugments: `team`, `limit` and
        `start`. `team` is used for querying the projects of one team by
        its name, which the user is one of its memebers. `limit` is
        the max number of items sent back to the client. `start` is the
        starting index of the querying results.

        Only authenticated user/resouce owner can access by using access_token,
        and his/her scopes must include `projects`.

        The retrieved resource should always be related to the user, and it is
        not allowed to access others' projects or other teams' projects.

        .. todo::
            restrict the response data and add default limits
        """
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
            team_name = self.get_argument('team', None)
            limit = self.get_argument('limit', None)
            start = self.get_argument('start', None)
            try:
                team_name = parse_path(team_name)[0]
            except IndexError:
                team_name = None
            try:
                limit = int(limit)
            except Exception:
                limit = None
            try:
                start = int(start)
            except Exception:
                start = None
            if team_name:
                team = Team.objects(name=team_name).first()
                if not team:
                    self.raise404()
                if user not in team.members:
                    self.raise403()
                project = Project.objects(teams__in=[team])
            else:
                project = Project.objects(members__in=[user])
            if limit and start:
                project = project[start:start + limit]
            elif limit:
                project = project[:limit]
            elif start:
                project = project[start:]
            project_data = query_to_json(project, filter_set=_FILTER)
        self.write(project_data)

    @authenticated(scopes=['projects'])
    def post(self, *args, **kwargs):
        """Create a new project by providing the details about the project.
        If the validation and saving are successful, it response with the
        project data and 201 status.
        Otherwise, it gives 4XX status and error messages.
        """
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
        """Update a project by its name and other information.
        """
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
        """Delete a project by its name provided in URL.
        """
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

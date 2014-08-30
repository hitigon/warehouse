#!/usr/bin/env python
#
# @name: api/team.py
# @create: Apr. 25th, 2014
# @update: Aug. 29th, 2014
# @author: hitigon@gmail.com
from __future__ import print_function
from oauth.protector import authenticated
from base import BaseHandler
from utils import parse_listed_strs, parse_path
from utils import document_to_json, query_to_json
from models.user import User
from models.team import Team

_SUB_FILTER = {
    'password': False,
    'ip': False,
    'create_time': False,
    'login_time': False,
}

_FILTER = {
    'leader': _SUB_FILTER,
    'members': _SUB_FILTER,
}


class TeamHandler(BaseHandler):

    @authenticated(scopes=['teams'])
    def get(self, *args, **kwargs):
        if 'user' not in kwargs:
            self.raise401()

        user = kwargs['user']
        if args:
            path = parse_path(args[0])
            team = Team.objects(name=path[0]).first()
            if not team:
                self.raise404()
            team_data = document_to_json(team, filter_set=_FILTER)
        else:
            # username = self.get_argument('username', None)
            # try:
            #     username = parse_path(username)[0]
            # except IndexError:
            #     username = None
            # if username:
            #     user = User.objects(username=username).fisrt()
            limit = self.get_argument('limit', None)
            start = self.get_argument('start', None)
            try:
                limit = int(limit)
            except:
                limit = None
            try:
                start = int(start)
            except:
                start = None
            teams = Team.objects(members__in=[user])
            if limit and start:
                teams = teams[start: start+limit]
            elif limit:
                teams = teams[:limit]
            elif start:
                teams = teams[start:]
            team_data = query_to_json(teams, filter_set=_FILTER)
        self.write(team_data)

    @authenticated(scopes=['teams'])
    def post(self, *args, **kwargs):
        if 'user' not in kwargs or args:
            self.raise401()
        name = self.get_argument('name', None)
        description = self.get_argument('description', None)
        url = self.get_argument('url', None)
        leader = self.get_argument('leader', None)
        members = self.get_argument('members', None)
        tags = self.get_argument('tags', None)

        try:
            # todo - better arguments handler
            url = url.strip()
            url = url if url else None
            members_list = []
            team_leader = kwargs['user']
            if leader:
                team_leader = User.objects(username=leader).first()
            if members:
                for member in parse_listed_strs(members):
                    u = User.objects(username=member).first()
                    if not u or u == team_leader:
                        continue
                    members_list.append(u)
            members_list.append(team_leader)
            tags_list = parse_listed_strs(tags)
            team = Team(
                name=name, description=description,
                url=url, leader=team_leader,
                members=members_list, tags=tags_list)
            team.save()
            team_data = document_to_json(team, filter_set=_FILTER)
            self.set_status(201)
            self.write(team_data)
        except Exception as e:
            reason = e.message
            self.raise400(reason=reason)

    @authenticated(scopes=['teams'])
    def put(self, *args, **kwargs):
        if 'user' not in kwargs or not args:
            self.raise401()
        user = kwargs['user']
        path = parse_path(args[0])
        team = Team.objects(name=path[0]).first()
        if not team or user not in team.members:
            self.raise401()
        team_leader = team.leader
        update = {}
        name = self.get_argument('name', None)
        description = self.get_argument('description', None)
        url = self.get_argument('url', None)
        leader = self.get_argument('leader', None)
        members = self.get_argument('members', None)
        tags = self.get_argument('tags', None)
        if name:
            update['set__name'] = name
        if description:
            update['set__description'] = description
        if url:
            update['set__url'] = url
        if leader:
            team_leader = User.objects(username=leader).first()
            update['set__leader'] = team_leader
        if members:
            members_list = []
            for member in parse_listed_strs(members):
                u = User.objects(username=member).first()
                if not u or u == team_leader:
                    continue
                members_list.append(u)
            members_list.append(team_leader)
            update['set__members'] = members_list
        if tags:
            tags_list = parse_listed_strs(tags)
            update['set__tags'] = tags_list
        try:
            Team.objects(name=path[0]).update_one(**update)
            team = Team.objects(name=name or path[0]).first()
            team_data = document_to_json(team, filter_set=_FILTER)
            self.set_status(201)
            self.write(team_data)
        except Exception as e:
            reason = e.message
            self.raise400(reason=reason)

    @authenticated(scopes=['teams'])
    def delete(self, *args, **kwargs):
        if 'user' not in kwargs or not args:
            self.raise401()
        user = kwargs['user']
        path = parse_path(args[0])
        team = Team.objects(name=path[0]).first()
        if not team or user not in team.members:
            self.raise401()
        try:
            Team.objects(name=path[0]).delete()
            self.set_status(204)
            self.finish()
        except Exception as e:
            reason = e.message
            self.raise400(reason=reason)

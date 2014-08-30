#!/usr/bin/env python
#
# @name: api/repo.py
# @create: Apr. 22th, 2014
# @update: Aug. 29th, 2014
# @author: hitigon@gmail.com
from __future__ import print_function
import re
from utils import parse_listed_strs, parse_path
from utils import document_to_json, query_to_json
from base import BaseHandler
from oauth.protector import authenticated
from scm.git import GitRepo
from models.repo import Repo
from models.team import Team

_SUB_FILTER = {
    'password': False,
    'ip': False,
    'create_time': False,
    'login_time': False,
}

_FILTER = {
    'owner': _SUB_FILTER,
    'team': {
        'leader': _SUB_FILTER,
        'members': _SUB_FILTER,
    },
}


class RepoHandler(BaseHandler):

    @authenticated(scopes=['repos'])
    def get(self, *args, **kwargs):
        if 'user' not in kwargs:
            self.raise401()
        user = kwargs['user']
        repo_type = None
        repo_query = None
        repo_contents = None
        repo_branches = None
        repo_tags = None
        repo_info = None
        limit = self.get_argument('limit', None)
        start = self.get_argument('start', None)
        try:
            limit = int(limit)
        except:
            limit = None
        if args:
            # author = self.get_argument('author', None)
            path = parse_path(args[0])
            if not path:
                self.raise404()
            repo = Repo.objects(owner=user, name=path[0]).first()
            if repo:
                scm_repo = GitRepo(repo.path)
                repo_info = scm_repo.get_info()
                repo_branches, repo_tags = get_repo_branches_tags(scm_repo)
                repo_type, repo_query, repo_contents = get_repo_contents(
                    scm_repo, path[1:], limit=limit, start=start)
            if not repo_contents:
                self.raise404()
            repo_data = document_to_json(repo, filter_set=_FILTER)
        else:
            team_name = self.get_argument('team_name', None)
            try:
                start = int(start)
            except:
                start = None
            try:
                team_name = parse_path(team_name)[0]
            except IndexError:
                team_name = None
            if team_name:
                team = Team.objects(name=team_name).first()
                if not team:
                    self.raise404()
                if user not in team.member:
                    self.raise403()
                repos = Repo.objects(team=team)
            else:
                repos = Repo.objects(owner=user)
            if limit and start:
                repos = repos[start: start+limit]
            elif limit:
                repos = repos[:limit]
            elif start:
                repos = repos[start:]
            repo_data = query_to_json(repos, filter_set=_FILTER)
        if repo_type and repo_contents:
            repo_data['repo_info'] = repo_info
            repo_data['repo_type'] = repo_type
            repo_data['repo_query'] = repo_query
            repo_data['repo_branches'] = repo_branches
            repo_data['repo_tags'] = repo_tags
            repo_data['repo_contents'] = repo_contents
        self.write(repo_data)

    @authenticated(scopes=['repos'])
    def post(self, *args, **kwargs):
        name = self.get_argument('name', None)
        description = self.get_argument('description', None)
        path = self.get_argument('path', None)  # verify
        scm = self.get_argument('scm', None)
        team = self.get_argument('team', None)  # just for test
        tags = self.get_argument('tags', None)
        if 'user' not in kwargs:
            self.raise401()
        user = kwargs['user']
        tags_list = parse_listed_strs(tags)
        try:
            name = name.strip()
            name = name if name else None
            repo = Repo(name=name, description=description,
                        path=path, scm=scm, owner=user,
                        team=team, tags=tags_list)
            repo.save()
            repo_data = document_to_json(repo, filter_set=_FILTER)
            self.set_status(201)
            self.write(repo_data)
        except Exception as e:
            reason = e.message
            self.raise400(reason=reason)

    @authenticated(scopes=['repos'])
    def put(self,  *args, **kwargs):
        if 'user' not in kwargs or not args:
            self.raise401()
        name = self.get_argument('name', None)
        description = self.get_argument('description', None)
        path = self.get_argument('path', None)
        scm = self.get_argument('scm', None)
        team = self.get_argument('team', None)
        tags = self.get_argument('tags', None)
        user = kwargs['user']
        update = {}
        if name:
            update['set__name'] = name
        if description:
            update['set__description'] = description
        if path:
            update['set__path'] = path
        if scm:
            update['set__scm'] = scm
        if team:
            update['set__team'] = team
        if tags:
            tags_list = parse_listed_strs(tags)
            update['set__tags'] = tags_list
        try:
            path = parse_path(args[0])
            Repo.objects(owner=user, name=path[0]).update_one(**update)
            repo = Repo.objects(owner=user, name=name or path[0]).first()
            repo_data = document_to_json(repo, filter_set=_FILTER)
            self.set_status(201)
            self.write(repo_data)
        except Exception as e:
            reason = e.message
            self.raise400(reason=reason)

    @authenticated(scopes=['repos'])
    def delete(self, *args, **kwargs):
        if 'user' not in kwargs or not args:
            self.raise401()
        try:
            user = kwargs['user']
            path = parse_path(args[0])
            Repo.objects(owner=user, name=path[0]).delete()
            self.set_status(204)
            self.finish()
        except Exception as e:
            reason = e.message
            self.raise400(reason=reason)


def get_repo_contents(scm_repo, fields, **kwargs):
    try:
        obj_type = fields[0]
    except IndexError:
        return 'tree', 'master', scm_repo.get_current_root()
    response = None
    current_query = None
    if obj_type == 'tree' or obj_type == 'blob':
        if len(fields) >= 2:
            query = fields[1]
            # no remote branch is allowed
            branch = scm_repo.check_branch(query)
            tag = scm_repo.check_tag(query)
            if branch:
                commit = scm_repo.get_commit_by_branch(branch)
            elif tag:
                commit = scm_repo.get_commit_by_tag(tag)
            else:
                # query is a commit id
                commit = scm_repo.get_commit(query)
            if commit:
                current_query = query
                fields = fields[2:]
                if obj_type == 'tree':
                    response = scm_repo.get_tree_by_commit(commit, fields)
                else:
                    response = scm_repo.get_blob_by_commit(commit, fields)
    elif obj_type == 'commit' and len(fields) >= 2:
        patches = scm_repo.get_patches(fields[1])
        response = scm_repo.get_commit(fields[1])
        response['patches'] = patches
    elif obj_type == 'commits':
        limit = kwargs['limit'] if 'limit' in kwargs else None
        start = kwargs['start'] if 'start' in kwargs else None
        # if limit:
        #     try:
        #         limit = int(limit)
        #     except:
        #         limit = 10
        if limit and start:
            response = scm_repo.get_commits(limit, start)
        elif start:
            response = scm_repo.get_commits(oid_or_commit=start)
        elif limit:
            response = scm_repo.get_commits(depth=limit)
        else:
            response = scm_repo.get_commits()
        print(response)
    return obj_type, current_query, response


def get_repo_branches_tags(scm_repo):
    branches = []
    tags = []
    try:
        refs = scm_repo.get_all_references()
        br = re.compile('^refs/heads/')
        tr = re.compile('^refs/tags/')
        branches = map(lambda s: s[11:], filter(lambda r: br.match(r), refs))
        tags = map(lambda s: s[10:], filter(lambda r: tr.match(r), refs))
    except Exception as e:
        print(e)
    return branches, tags

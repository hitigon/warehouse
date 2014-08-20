#!/usr/bin/env python
#
# @name: api/repo.py
# @create: Apr. 22th, 2014
# @update: Aug. 20th, 2014
# @author: hitigon@gmail.com
from __future__ import print_function
import re
import json
from scm.git import GitRepo
from libs.utils import parse_listed_strs, parse_path
from models.repo import Repo
from oauth.protector import authenticated
from . import BaseHandler


class RepoHandler(BaseHandler):

    @authenticated(scopes=['repos'])
    def get(self, *args, **kwargs):
        # an authenticated user can read her/his own repos, team's repos
        # plus any repos in his/her projects
        # what about team members, and project members' repos? TBD
        # /repos
        # /repos/:id/../../.../
        # /repos?username=
        # /repos?team=
        # /repos?project=
        # /repos?tag=
        # username = self.get_argument('username', None)
        # team = self.get_argument('team_name', None)
        # project = self.get_argument('project_name', None)
        if 'user' not in kwargs:
            self.raise401()
        user = kwargs['user']
        repo_type = None
        repo_query = None
        repo_contents = None
        repo_branches = None
        repo_tags = None
        repo_info = None
        if args:
            path = parse_path(args[0])
            if not path:
                self.raise404()
            repo = Repo.objects(owner=user, name=path[0]).first()
            if repo:
                scm_repo = GitRepo(repo.path)
                repo_info = scm_repo.get_info()
                repo_branches, repo_tags = get_repo_branches_tags(scm_repo)
                repo_type, repo_query, repo_contents = get_repo_contents(
                    scm_repo, path[1:])
            if not repo_contents:
                self.raise404()
        else:
            repo = Repo.objects(owner=user).all()
        repo_data = json.loads(repo.to_json())
        if repo_type and repo_contents:
            repo_data['repo_info'] = repo_info
            repo_data['repo_type'] = repo_type
            repo_data['repo_query'] = repo_query
            repo_data['repo_branches'] = repo_branches
            repo_data['repo_tags'] = repo_tags
            repo_data['repo_contents'] = repo_contents
        self.write(json.dumps(repo_data))

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
            repo_data = json.loads(repo.to_json())
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
        tags_list = parse_listed_strs(tags)
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
            update['set__tags'] = tags_list
        try:
            path = parse_path(args[0])
            Repo.objects(owner=user, name=path[0]).update_one(**update)
            repo = Repo.objects(owner=user, name=name or path[0]).first()
            repo_data = json.loads(repo.to_json())
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
            repo = Repo.objects(owner=user, name=path[0])
            if repo:
                repo.delete()
            self.set_status(204)
            self.finish()
        except Exception as e:
            reason = e.message
            self.raise400(reason=reason)


def get_repo_contents(scm_repo, fields):
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

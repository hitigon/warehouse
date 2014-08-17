#!/usr/bin/env python
#
# @name: api/repo.py
# @create: Apr. 22th, 2014
# @update: Aug. 17th, 2014
# @author: hitigon@gmail.com
from __future__ import print_function
import json
from scm.git import GitRepo
from libs.utils import parse_listed_strs, parse_path
from models.repo import Repo
from oauth.protector import authenticated
from . import BaseHandler
from . import CreateSuccess, QuerySuccess


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
        response = {}
        try:
            user = kwargs['user']
            repo_type = None
            repo_query = None
            repo_contents = None
            repo_branches = None
            repo_tags = None
            if len(args) > 0:
                path = parse_path(args[0])
                repo = Repo.objects(owner=user, name=path[0]).first()
                scm_repo = GitRepo(repo.path)
                repo_branches, repo_tags = get_repo_branches_tags(scm_repo)
                repo_type, repo_query, repo_contents = get_repo_contents(
                    scm_repo, path[1:])
            else:
                repo = Repo.objects(owner=user).all()
            repo_data = json.loads(repo.to_json())
            if repo_type and repo_contents:
                repo_data['repo_type'] = repo_type
                repo_data['repo_branches'] = repo_branches
                repo_data['repo_tags'] = repo_tags
                repo_data['repo_contents'] = repo_contents
                repo_data['repo_query'] = repo_query
            msg = 'Repo found'
            response = self.get_response(
                data=repo_data, success=QuerySuccess(msg))
        except Exception as e:
            response = self.get_response(error=e)
        print(response)
        self.write(response)

    @authenticated(scopes=['repos'])
    def post(self, *args, **kwargs):
        name = self.get_argument('name', None)
        description = self.get_argument('description', None)
        path = self.get_argument('path', None)  # verify
        scm = self.get_argument('scm', None)
        team = self.get_argument('team', None)  # just for test
        tags = self.get_argument('tags', None)
        response = {}
        try:
            user = kwargs['user']
            tags_list = parse_listed_strs(tags)
            repo = Repo(name=name, description=description,
                        path=path, scm=scm, owner=user,
                        team=team, tags=tags_list)
            repo.save()
            repo_data = json.loads(repo.to_json())
            msg = 'Repo added'
            response = self.get_response(
                data=repo_data, success=CreateSuccess(msg))
        except Exception as e:
            response = self.get_response(error=e)
        self.write(response)

    def put(self,  *args, **kwargs):
        # name = self.get_argument('name', None)
        # path = self.get_argument('path', None)
        # scm = self.get_argument('scm', None)
        # tags = self.get_argument('tags', None)

        # update = {}
        # if name:
        #     update['name'] = name
        # if path:
        #     update['path'] = path
        # if scm:
        #     update['scm'] = scm
        # if tags:
        #     update['tags'] = [str(tag).strip() for tag in tags.split(',')]
        # document = {'$set': update}
        # if repo.update(query_id, document):
        #     data = repo.query(query_id)
        #     response = get_respmsg(1001, data)
        # else:
        #     response = get_respmsg(-1001)
        response = {}
        self.write(response)

    def delete(self, *args, **kwargs):
        # if ObjectId.is_valid(query_id):
        #     spec = query_id
        # else:
        #     spec = {'name': query_id}
        # if repo.delete(spec):
        #     response = get_respmsg(1002)
        # else:
        #     response = get_respmsg(-1002)
        response = {}
        self.write(response)


def get_repo_contents(scm_repo, fields):
    try:
        obj_type = fields[0]
    except IndexError:
        return 'tree', 'master', scm_repo.get_current_root()
    response = None
    current_query = None
    if obj_type == 'info':
        response = scm_repo.get_info()
    elif obj_type == 'tree' or obj_type == 'blob':
        if len(fields) >= 2:
            query = fields[1]
            # no remote branch is allowed
            branch = scm_repo.check_branch(query)
            tag = scm_repo.check_tag(query)
            if branch:
                commit = scm_repo.get_commit_by_branch(branch)
                current_query = branch.branch_name[11:]
            elif tag:
                commit = scm_repo.get_commit_by_tag(tag)
                current_query = tag.name[10:]
            else:
                # query is a commit id
                commit = scm_repo.get_commit(query)
                current_query = query
            fields = fields[2:]
            if obj_type == 'tree':
                response = scm_repo.get_tree_by_commit(commit, fields)
            else:
                response = scm_repo.get_blob_by_commit(commit, fields)
    elif obj_type == 'commit' and len(fields) >= 2:
        response = scm_repo.get_commit(fields[1])
    elif obj_type == 'patch' and len(fields) == 2:
        response = scm_repo.get_patches(fields[1])
    return obj_type, current_query, response


def get_repo_branches_tags(scm_repo):
    refs = scm_repo.get_all_references()
    branches = []
    tags = []
    try:
        for ref in refs:
            if 'refs/heads/' in ref:
                branches.append(ref[11:])
            elif 'refs/tags/' in ref:
                tags.append(ref[10:])
    except Exception as e:
        print(e)
    return branches, tags

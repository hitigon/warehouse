#!/usr/bin/env python
#
# @name: api/repo.py
# @date: Apr. 22th, 2014
# @author: hitigon@gmail.com
from __future__ import print_function
import tornado.web
from bson import ObjectId
from model import repo
from scm.git import GitRepo
from . import get_respmsg


class RepoHandler(tornado.web.RequestHandler):

    def __get_repo_contents(self, scm_repo, path):
        fields = path.strip().split('/')
        if not fields or len(fields) <= 0:
            return None

        if fields[-1] == '':
            fields = fields[0:-1]

        obj_type = fields[0]
        response = None
        if obj_type == 'info':
            response = scm_repo.get_info()
        elif obj_type == 'tree' or obj_type == 'blob':
            if len(fields) > 2 or len(fields) == 2 and obj_type == 'tree':
                query = fields[1]
                if scm_repo.check_branch(query):
                    commit = scm_repo.get_commit_by_branch(query)
                elif scm_repo.check_tag(query):
                    commit = scm_repo.get_commit_by_tag(query)
                else:
                    commit = scm_repo.get_commit(query)
                fields = fields[2:]
                if obj_type == 'tree':
                    response = scm_repo.get_tree_by_commit(commit, fields)
                else:
                    response = scm_repo.get_blob_by_commit(commit, fields)
        elif obj_type == 'commit' and len(fields) >= 2:
            query = fields[1]
            if scm_repo.check_branch(query):
                response = scm_repo.get_commits_by_branch(query, fields[2:])
            elif scm_repo.check_tag(query):
                response = scm_repo.get_commits_by_tag(query, fields[2:])
            else:
                response = scm_repo.get_commit(query)
        elif obj_type == 'patch' and len(fields) == 2:
            response = scm_repo.get_patches(fields[1])
        return response

    def get(self, query_id=None, path=None):
        if query_id:
            if ObjectId.is_valid(query_id):
                response = repo.query(query_id)
            else:
                spec = {'name': query_id}
                response = repo.query(spec)
            if response and path:
                repo_path = response['path']
                scm_repo = GitRepo(repo_path)
                response = self.__get_repo_contents(scm_repo, path)
        else:
            response = repo.query_all()

        if response is None:
                response = {}
        self.write(response)

    def post(self):
        name = self.get_argument('name', None)
        path = self.get_argument('path', None)
        scm = self.get_argument('scm', 'git')
        project = self.get_argument('project', None)
        tags = self.get_argument('tags', None)

        if name is None or path is None:
            response = get_respmsg(-1003)
        else:
            result = repo.create(name, path, scm, project, tags)
            if result:
                response = get_respmsg(1000)
            else:
                response = get_respmsg(-1000)
        self.write(response)

    def put(self, query_id):
        name = self.get_argument('name', None)
        path = self.get_argument('path', None)
        scm = self.get_argument('scm', None)
        project = self.get_argument('project', None)
        tags = self.get_argument('tags', None)

        update = {}
        if name:
            update['name'] = name
        if path:
            update['path'] = path
        if scm:
            update['scm'] = scm
        if project and ObjectId.is_valid(project):
            update['project'] = ObjectId(project)
        if tags:
            update['tags'] = [str(tag).strip() for tag in tags.split(',')]
        document = {'$set': update}
        if repo.update(query_id, document):
            response = get_respmsg(1001)
        else:
            response = get_respmsg(-1001)

        self.write(response)

    def delete(self, query_id):
        if ObjectId.is_valid(query_id):
            spec = query_id
        else:
            spec = {'name': query_id}
        if repo.delete(spec):
            response = get_respmsg(1002)
        else:
            response = get_respmsg(-1002)
        self.write(response)

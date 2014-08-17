#!/usr/bin/env python
#
# @name: scm/git.py
# @date: Apr. 21th, 2014
# @author: hitigon@gmail.com
from __future__ import unicode_literals
from __future__ import print_function
from pygit2 import Repository
from pygit2 import Commit
from pygit2 import GIT_OBJ_COMMIT, GIT_OBJ_TREE
from pygit2 import GIT_OBJ_BLOB, GIT_OBJ_TAG
from pygit2 import GIT_BRANCH_LOCAL
from pygit2 import Settings


def tree_walker(repo, oid, pid=None):
    ''' tree walker '''
    if oid is None:
        return None
    result = []
    try:
        tree = repo.get(oid)
        if tree and tree.type == GIT_OBJ_TREE:
            for entry in tree:
                result.append((str(entry.id), str(pid), entry.name))
                child = repo.get(entry.id)
                if child.type == GIT_OBJ_TREE:
                    result += tree_walker(child.id, entry.id)
    except ValueError as e:
        print(e)
    return result


class GitRepo(object):

    ''' git repo class '''

    def __init__(self, path):
        try:
            self.__repo = Repository(path)
            # print('____', float(Settings().mwindow_size)/float(1024))
        except KeyError as e:
            self.__repo = None
            print(e)

    def get_info(self):
        if self.__repo is None:
            return None
        signature = self.__repo.default_signature
        result = {
            'path': self.__repo.path,
            'workdir': self.__repo.workdir,
            'bare': self.__repo.is_bare,
            'empty': self.__repo.is_empty,
            'name': signature.name,
            'email': signature.email,
            'time': signature.time,
            'offset': signature.offset,
        }
        return result

    def get_reference(self, name):
        if self.__repo is None:
            return None
        ref = None
        try:
            ref = self.__repo.lookup_reference(name)
        except KeyError as e:
            print(e)
        except ValueError as e:
            print(e)
        return ref

    def get_all_branches(self, branch_type=None):
        if not self.__repo:
            return None
        if branch_type:
            return self.__repo.listall_braches(branch_type)
        return self.__repo.listall_braches()

    def get_branch(self, name, branch_type=GIT_BRANCH_LOCAL):
        if self.__repo is None:
            return None
        return self.__repo.lookup_branch(name, branch_type)

    def check_branch(self, name, branch_type=GIT_BRANCH_LOCAL):
        return self.get_branch(name, branch_type) is not None

    def get_current_commit(self):
        if self.__repo is None:
            return None
        commit = self.__repo.revparse_single('HEAD')
        return self.get_commit(commit)

    def get_commit_by_branch(self, name):
        if self.__repo is None:
            return None
        if self.check_branch(name):
            ref = self.get_reference('refs/heads/' + name)
            if ref:
                commit = ref.target
                return self.get_commit(commit)
        return None

    def get_commit_by_tag(self, name):
        if self.__repo is None:
            return None
        ref = self.get_reference('refs/tags/' + name)
        if ref:
                commit = ref.target
                return self.get_commit(commit)
        return None

    def get_commit(self, oid_or_commit):
        ''' return a commit w/ json '''
        if self.__repo is None or oid_or_commit is None:
            return None
        try:
            commit = oid_or_commit
            if not isinstance(oid_or_commit, Commit):
                commit = self.__repo.get(oid_or_commit)
            if commit is not None and commit.type == GIT_OBJ_COMMIT:
                result = {
                    'id': str(commit.id),
                    'author': commit.author.name,
                    'commiter': commit.committer.name,
                    'message': commit.message,
                    'message_encoding': commit.message_encoding,
                    'tree': str(commit.tree_id),
                    'parent': [str(pid) for pid in commit.parent_ids],
                    'time': str(commit.commit_time),
                    'time_offset': str(commit.commit_time_offset),
                }
                return result
        except ValueError as e:
            print(e)
        return None

    def get_commits(self, oid_or_commit):
        result = {}
        commit = self.get_commit(oid_or_commit)
        result[commit['id']] = commit
        if commit and commit['parent']:
            for parent in commit['parent']:
                    result.update(self.get_commits(parent))
        return result

    def get_commits_by_branch(self, name, path=None):
        if self.__repo is None:
            return None
        if self.check_branch(name):
            ref = self.get_reference('refs/heads/' + name)
            if ref:
                commit = ref.target
                commits = self.get_commits(commit)
                result = {}
                for key, val in commits.items():
                    if self.check_commit_by_path(val, path):
                        result[key] = val
                return result
        return None

    def get_commits_by_tag(self, name, path=None):
        if self.__repo is None:
            return None
        ref = self.get_reference('refs/tags/' + name)
        if ref:
                commit = ref.target
                commits = self.get_commits(commit)
                result = {}
                for key, val in commits.items():
                    if self.check_commit_by_path(val, path):
                        result[key] = val
                return result
        return None

    def check_commit_by_path(self, commit, path):
        if commit is None:
            return False
        if path is None or len(path) == 0:
            return True
        result = self.get_tree(commit['tree'])

        if not isinstance(path, list):
            path = path.strip().split('/')

        for name in path:
            name = name.strip()
            if name in result:
                oid = result[name]
                result = self.get_tree(oid)

                if not result:
                    result = self.get_blob(oid)
        return result is not None

    def get_tree(self, oid, ppath=None):
        if not self.__repo:
            return None
        try:
            tree = self.__repo.get(oid)
            if tree and tree.type == GIT_OBJ_TREE:
                result = {}
                for entry in tree:
                    item = {
                        'id': str(entry.id)
                    }
                    obj = self.__repo.get(entry.id)
                    if obj.type == GIT_OBJ_BLOB:
                        item['type'] = 'blob'
                    elif obj.type == GIT_OBJ_TREE:
                        item['type'] = 'tree'
                    item['ppath'] = ppath
                    result[entry.name] = item
                return result
        except ValueError as e:
            print(e)
        return None

    def get_tree_by_commit(self, commit, path=None):
        if not commit:
            return None
        result = self.get_tree(commit['tree'])
        if not path:
            return result

        # if not isinstance(path, list):
        #     path = path.strip().split('/')

        try:
            for name in path:
                oid = result[name]['id']
                p = result[name]['ppath']
                p = name if not p else p + '/' + name
                result = self.get_tree(oid, p)
                if not result:
                    break
        except KeyError as e:
            print(e)
            result = None
        return result

    def get_current_root(self):
        tree = self.get_current_commit()
        if tree:
            return self.get_tree(tree['tree'])
        return None

    def get_whole_tree(self, oid):
        ''' tree w/ json '''
        if not self.__repo:
            return None
        result = tree_walker(self.__repo, oid)
        return result

    def get_blob(self, oid):
        ''' blob w/ json '''
        if not self.__repo or not oid:
            return None
        try:
            blob = self.__repo.get(oid)
            if blob and blob.type == GIT_OBJ_BLOB:
                content = blob.is_binary and None or blob.data.decode(
                    'utf8', 'ignore')
                result = {
                    'id': str(blob.id),
                    'content': content,
                    'size': blob.size,
                }
                return result
        except ValueError as e:
            print(e)
        return None

    def get_blob_by_commit(self, commit, path=None):

        try:
            tree = self.get_tree_by_commit(commit, path[:-1])
            oid = tree[path[-1]]['id']
            result = self.get_blob(oid)
            return result
        except KeyError:
            return None

    def get_tag(self, oid):
        ''' blob w/ json '''
        if self.__repo is None or oid is None:
            return None
        try:
            tag = self.__repo.get(oid)
            if tag is not None and tag.type == GIT_OBJ_TAG:
                result = {
                    'id': str(oid),
                    'name': tag.name,
                    'target': str(tag.target.id),
                    'tagger': tag.tagger,
                    'message': tag.message,
                }
                return result
        except ValueError as e:
            print(e)
        return None

    def check_tag(self, name):
        return self.get_reference(name) is not None

    def get_patches(self, a, b=None):
        if self.__repo is None or a is None:
            return None

        tree_a = self.__repo.get(a).tree

        if not tree_a:
            return None

        if b:
            tree_b = self.__repo.get(b).tree
        else:
            tree_b = self.__repo.get(a).parents[0].tree

        diff = self.__repo.diff(tree_a, tree_b)
        result = {}
        idx = 0
        for patch in diff:
            i = 0
            p = {
                'old_file_path': patch.old_file_path,
                'new_file_path': patch.new_file_path,
                'old_oid': str(patch.old_oid),
                'new_oid': str(patch.new_oid),
                'status': patch.status,
                'similarity': patch.similarity,
                'additions': patch.additions,
                'deletions': patch.deletions,
                'binary': patch.is_binary,
                'hunks': {},
            }
            for hunk in patch.hunks:
                h = {
                    'old_start': hunk.old_start,
                    'old_lines': hunk.old_lines,
                    'new_start': hunk.new_start,
                    'new_lines': hunk.new_lines,
                    'lines': hunk.lines,
                }
                p['hunks'][i] = h
                i += 1
            result[idx] = p
            idx += 1
        return result

if __name__ == '__main__':
    pass

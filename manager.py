#!/usr/bin/env python
#
# @name: manager.py
# @create: Apr. 22th, 2014
# @update: Aug. 21th, 2014
# @author: hitigon@gmail.com
import logging
import sys
import tornado.ioloop
import tornado.web
from mongoengine import connect
from api import client
from api import auth
from api import user
from api import repo
from api import project
from api import task

settings = {
    'debug': True,
    'autoreload': True
}


application = tornado.web.Application([
    (r'/authorize/?', auth.AuthHandler),
    (r'/token/?', auth.TokenHandler),
    #(r'/signin/?', user.SigninHandler),
    (r'/signup/?', user.RegisterHandler),
    (r'/profile/?', user.ProfileHandler),
    (r'/profile/([\w.]+)/?', user.ProfileHandler),
    # (r'/users/([\w.]+)/(edit|delete)/?', user.UserHandler),
    (r'/repos/?', repo.RepoHandler),
    (r'/repos/([\w\-._/]+)+', repo.RepoHandler),
    #(r"/repos/([\w.]+)/([\w.@/]+)/?", repo.RepoHandler),
    (r'/projects/?', project.ProjectHandler),
    (r'/projects/([\w.]+)/?', project.ProjectHandler),
    # (r'/projects/(user|team)/([\w.]+)/?', project.ProjectHandler),
    (r"/tasks/?", task.TaskHandler),
    #(r"/tasks/([\w.]+)/?", task.TaskHandler),
    (r'/clients/?', client.ClientHandler),
], **settings)

if __name__ == '__main__':
    log = logging.getLogger('oauthlib')
    log.addHandler(logging.StreamHandler(sys.stdout))
    log.setLevel(logging.DEBUG)
    connect('orm')
    application.listen(8000)
    tornado.ioloop.IOLoop.instance().start()

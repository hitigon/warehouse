#!/usr/bin/env python
#
# @name: manager.py
# @date: Apr. 22th, 2014
# @author: hitigon@gmail.com
import logging
import sys
import tornado.ioloop
import tornado.web
from mongoengine import connect
from api import client
from api import auth
#from lib import util
from api import user
from api import repo
from api import project
#from api import task

settings = {
    #'cookie_secret': util.create_cookie_secret(),
    #'login_url': '/login',
    'debug': True,
    'autoreload': True
}


application = tornado.web.Application([
    (r'/authorize/?', auth.AuthHandler),
    (r'/token/?', auth.TokenHandler),
    #(r'/signin/?', user.SigninHandler),
    (r'/signup/?', user.SignupHandler),
    (r'/users/?', user.UserHandler),
    (r'/users/([\w.]+)/?', user.UserHandler),
    (r'/users/([\w.]+)/(edit|delete)/?', user.UserHandler),
    (r'/repos/?', repo.RepoHandler),
    (r'/repos/([\w\-._/]+)+', repo.RepoHandler),
    #(r"/repos/([\w.]+)/([\w.@/]+)/?", repo.RepoHandler),
    (r'/projects/?', project.ProjectHandler),
    (r'/projects/([\w.]+)/?', project.ProjectHandler),
    (r'/projects/(user|team)/([\w.]+)/?', project.ProjectHandler),
    #(r"/tasks/?", task.TaskHandler),
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

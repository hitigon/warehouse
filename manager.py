#!/usr/bin/env python
#
# @name: manager.py
# @date: Apr. 22th, 2014
# @author: hitigon@gmail.com
import tornado.ioloop
import tornado.web
from lib import util
from api import repo
from api import user

settings = {
    'cookie_secret': util.create_cookie_secret(),
    'login_url': '/login',
    'debug': True,
}


application = tornado.web.Application([
    (r"/login/?", user.LoginHandler),
    (r"/user/?", user.UserHandler),
    (r"/user/([\w.]+)/?", user.UserHandler),
    (r"/repo/?", repo.RepoHandler),
    (r"/repo/([\w.]+)/?", repo.RepoHandler),
    (r"/repo/([\w.]+)/([\w.@/]+)/?", repo.RepoHandler),
], **settings)

if __name__ == "__main__":
    application.listen(8000)
    tornado.ioloop.IOLoop.instance().start()

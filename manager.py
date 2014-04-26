#!/usr/bin/env python
#
# @name: manager.py
# @date: Apr. 22th, 2014
# @author: hitigon@gmail.com
import tornado.ioloop
import tornado.web
from api import repo


application = tornado.web.Application([
    (r"/repo/?", repo.RepoHandler),
    (r"/repo/([\w.]+)/?", repo.RepoHandler),
    (r"/repo/([\w.]+)/([\w.@/]+)/?", repo.RepoHandler),
], debug=True)

if __name__ == "__main__":
    application.listen(8000)
    tornado.ioloop.IOLoop.instance().start()

#!/usr/bin/env python
#
# @name: api/project.py
# @date: Apr. 25th, 2014
# @author: hitigon@gmail.com
from __future__ import print_function
import tornado.web
from bson import ObjectId
from model import repo
from . import get_respmsg


class RepoHandler(tornado.web.RequestHandler):
    pass

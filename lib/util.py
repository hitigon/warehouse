#!/usr/bin/env python
#
# @name: lib/util.py
# @date: Apr. 27th, 2014
# @author: hitigon@gmail.com
import time
import calendar
import base64
import uuid


def get_utc_timestamp():
    return calendar.timegm(time.gmtime())


def create_cookie_secret():
    return base64.b64encode(uuid.uuid4().bytes + uuid.uuid4().bytes)

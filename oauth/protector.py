#!/usr/bin/env python
#
# @name: oauth/validator.py
# @create: Aug. 14th, 2014
# @update: Aug. 14th, 2014
# @author: hitigon@gmail.com
from __future__ import print_function
import functools


def authenticated(scopes=None):
    def _auth(f):
        @functools.wraps(f)
        def wrapper(self, *args, **kwargs):
            try:
                scopes_list = scopes(self, *args, **kwargs)
            except TypeError:
                scopes_list = scopes
            base_uri, uri = self.get_uri()
            http_method = self.get_method()
            body = self.get_body()
            headers = self.get_headers()
            access_token = self.get_argument('access_token', None)
            # refresh_token = self.get_argument('refresh_token', None)
            # print(access_token)
            if not access_token:
                self.raise403()

            valid, r = self.endpoint.verify_request(
                uri, http_method, body, headers, scopes_list)
            if valid:
                update = {'user': r.user}
                kwargs.update(update)
                return f(self, *args, **kwargs)
            else:
                self.raise403()
        return wrapper

    return _auth

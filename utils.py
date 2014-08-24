#!/usr/bin/env python
#
# @name: utils.py
# @create: Apr. 27th, 2014
# @update: Aug. 23th, 2014
# @author: hitigon@gmail.com
import time
import json
import re
import calendar
import base64
import uuid
import hashlib
import random
import config
import pickle
import bcrypt
from bson.objectid import ObjectId
from datetime import datetime, timedelta
from bson.binary import Binary
from oauthlib.common import Request
from mongoengine import Document, QuerySet, EmbeddedDocument


def get_utc_time(seconds=0):
    return datetime.utcnow() + timedelta(0, seconds)


def get_utc_timestamp():
    return calendar.timegm(time.gmtime())


def datetime_to_timestamp(dt):
    return time.mktime(dt.timetuple())


def create_cookie_secret():
    return create_secret()


def create_uuid():
    return str(uuid.uuid4())


def create_id():
    s = hashlib.sha256(str(random.getrandbits(256))).digest()
    chars = random.choice(['rA', 'aZ', 'gQ', 'hH', 'hG', 'aR', 'DD'])
    return base64.b64encode(s, chars).rstrip('==')


def create_secret():
    return base64.b64encode(uuid.uuid4().bytes + uuid.uuid4().bytes)


def create_password(password):
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt())


def decode_basic_auth(s, decode=False):
    v = s.split()[1]
    if decode:
        return base64.b64decode(v)
    else:
        return v


def get_uri(data):
    protocol = data['protocol']
    base_uri = protocol + '://' + data['host']
    base_uri += ':' + \
        str(data[
            'port']) if protocol == 'http' or protocol == 'https' else ''
    return base_uri


def get_base_uri():
    return get_uri(config.base)


def get_auth_base_uri():
    return get_uri(config.auth)


def request_to_binary(request):
    store = {
        'uri': request.uri,
        'headers': request.headers,
        'body': request.body,
        'http_method': request.http_method,
    }
    return Binary(pickle.dumps(store))


def binary_to_request(binary):
    store = pickle.loads(str(binary))
    return Request(uri=store['uri'], http_method=store['http_method'],
                   headers=store['headers'], body=store['body'])


def parse_listed_strs(strs, delim=None):
    # parse tags, uris
    if not strs:
        return []
    result = []
    for sub in re.split(delim or ';|,| |\n', strs):
        sub = sub.strip()
        if len(sub) > 0:
            result.append(sub)
    return result


def parse_path(s):
    return parse_listed_strs(s, '/')


def convert_document(obj, filter_set=None):
    if isinstance(obj, Document) or isinstance(obj, EmbeddedDocument):
        result = {}
        for field in obj:
            item = obj[field]
            if filter_set and field in filter_set:
                if filter_set[field]:
                    result[field] = convert_document(item, filter_set[field])
                else:
                    continue
            else:
                result[field] = convert_document(item, filter_set)
        return result
    elif isinstance(obj, list):
        result = []
        for item in obj:
            result.append(convert_document(item, filter_set))
        return result
    elif isinstance(obj, dict):
        result = {}
        for k, v in obj.items():
            result[k] = convert_document(v, filter_set)
        return result
    elif isinstance(obj, ObjectId):
        return str(obj)
    elif isinstance(obj, datetime):
        return datetime_to_timestamp(obj)
    else:
        return obj


def document_to_json(obj, default_deref=False, filter_set=None):
    if default_deref and isinstance(obj, Document):
        return obj.to_json()
    return convert_document(obj, filter_set)


def query_to_json(query, default_deref=False, filter_set=None):
    if not query:
        return json.dumps([])
    if default_deref and isinstance(query, QuerySet):
        return query.to_json()
    result = []
    for doc in query:
        result.append(convert_document(doc, filter_set))
    return json.dumps(result)

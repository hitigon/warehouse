#!/usr/bin/env python
#
# @name: utils.py
# @create: Apr. 27th, 2014
# @update: Aug. 21th, 2014
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
from mongoengine import Document


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


def decode_basic_auth(s):
    return base64.b64decode(s.split()[1])


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


def convert_document(obj):
    if isinstance(obj, Document):
        result = {}
        for field in obj:
            item = obj[field]
            result[field] = convert_document(item)
        return result
    elif isinstance(obj, list):
        result = []
        for item in obj:
            result.append(convert_document(item))
        return result
    elif isinstance(obj, dict):
        result = {}
        for k, v in obj.items():
            result[k] = convert_document(v)
        return result
    elif isinstance(obj, ObjectId):
        return str(obj)
    elif isinstance(obj, datetime):
        return datetime_to_timestamp(obj)
    else:
        return obj


def convert_query(query_set):
    if not query_set:
        return json.dumps([])
    result = []
    for document in query_set:
        result.append(convert_document(document))
    return json.dumps(result)


def document_only_filter(doc, filter_set):
    if not doc or not isinstance(doc, Document):
        return None
    result = {}
    for field in doc:
        if field in filter_set:
            result[field] = convert_document(doc[field])
    return result

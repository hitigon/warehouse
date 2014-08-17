#!/usr/bin/env python
#
# @name: lib/morm/connection.py
# @date: Aug. 7th, 2014
# @author: hitigon@gmail.com
from __future__ import print_function
import logging
from pymongo import MongoClient


_dbs = {}
_connections = {}
_configs = {}

DEFAULT_OPTIONS = ['host', 'port', 'max_pool_size', 'document_class',
                   'tz_ware', 'socketTimeoutMS', 'connectTimeoutMS',
                   'waitQueueTimeoutMS', 'waitQueueMultiple',
                   'auto_start_request', 'use_greenlets', 'w',
                   'wtimeout', 'j', 'fsync', 'replicaSet',
                   'read_preference', 'tag_sets', 'ssl', 'ssl_keyfile',
                   'ssl_certfile', 'ssl_cert_reqs', 'ssl_ca_certs']


logging.basicConfig()
logger = logging.getLogger('MORM')


class ConnectionError(Exception):
    pass


def validate_options(options, default):
    validated = set(default)

    for k in options.keys():
        if k not in validated:
            del options[k]
            #Logger.warning('Unknow option found in ')
            logger.warning('Unknow option found: %r', k)


def disconnect(name):
    global _connections
    global _dbs
    if name in _connections:
        _connections[name].disconnect()
        del _connections[name]
    if name in _dbs:
        del _dbs[name]


def register_connection(name, **kwargs):
    global _configs
    global _connections

    settings = {
        'host': 'localhost',
        'port': 27017,
    }

    settings.update(**kwargs)
    validate_options(settings, DEFAULT_OPTIONS)

    # do not support mongodb_uri and multiple nodes for now
    #if 'host' in settings and '://' in settings['host']:
    #    uri_dict = uri_parser.parse_uri(settings['host'])

    _configs[name] = settings
    conn = None
    try:
        conn = MongoClient(**settings)
        _connections[name] = conn
    except Exception:
        raise ConnectionError('Cannot connect to mongodb')
    return conn


def connect(name, **kwargs):
    global _connections

    if name in _connections:
        return _connections[name]

    register_connection(name, **kwargs)


def get_connection(name):
    global _connections

    if name not in _connections:
        return
    return _connections[name]


def get_db(name):
    global _dbs

    if name not in _dbs:
        try:
            conn = get_connection(name)
            db = conn[name]
            _dbs[name] = db
        except Exception:
            raise ConnectionError('Cannot connect to database %s' % name)

    return _dbs[name]


if __name__ == '__main__':
    #connect('warehouse', test=112)
    #get_db('warehouse')
    pass

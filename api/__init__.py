#!/usr/bin/env python
#
# @name: __init__.py
# @date: Apr. 22th, 2014
# @author: hitigon@gmail.com

RESP_MSG = {
    1000: 'create successfully',
    1001: 'update successfully',
    1002: 'delete successfully',
    -1000: 'create failed',
    -1001: 'update failed',
    -1002: 'delete failed',
    -1003: 'incomplete fields',
}


def get_respmsg(code):
    if code in RESP_MSG:
        return {code: RESP_MSG[code]}
    else:
        return {0: 'unknown'}

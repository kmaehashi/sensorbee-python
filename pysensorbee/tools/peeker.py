# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, print_function, unicode_literals


class Peeker(object):
    def __init__(self, api):
        self._api = api

    def peek(self, topology, stream, count, expressions='*'):
        limit = ''
        if count != 0:
            limit = '[LIMIT {0}]'.format(count)
        query = 'SELECT RSTREAM {0} {1} FROM {2} [RANGE 1 TUPLES];'.format(limit, expressions, stream)
        for data in self._api.query(topology, query):
            yield data

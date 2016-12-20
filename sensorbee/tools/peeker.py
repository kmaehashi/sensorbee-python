# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, print_function, unicode_literals


class Peeker(object):
    def __init__(self, api):
        self._api = api

    def peek(self, topology, stream):
        query = 'SELECT RSTREAM * FROM {0} [RANGE 1 TUPLES];'.format(stream)
        for data in self._api.query(topology, query):
            return data

# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, print_function, unicode_literals


class Spider(object):
    def __init__(self, api):
        self._api = api

    def get(self):
        status = {
            'runtime_status': self.get_runtime_status(),
            'topologies': {},
        }
        for t in map(lambda x: x['name'], self._api.topologies()['topologies']):
            status['topologies'][t] = self.get_topology_status(t)
        return status

    def get_runtime_status(self):
        return self._api.runtime_status()

    def get_topology_status(self, t):
        status = {
            'sources': {},
            'streams': {},
            'sinks': {},
        }
        for s in map(lambda x: x['name'], self._api.sources(t)['sources']):
            status['sources'][s] = self._api.source(t, s)['source']
        for s in map(lambda x: x['name'], self._api.streams(t)['streams']):
            status['streams'][s] = self._api.stream(t, s)['stream']
        for s in map(lambda x: x['name'], self._api.sinks(t)['sinks']):
            status['sinks'][s] = self._api.sink(t, s)['sink']
        return status

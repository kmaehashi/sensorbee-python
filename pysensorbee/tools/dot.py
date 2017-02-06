# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, print_function, unicode_literals


class DotView(object):
    def __init__(self, api):
        self._api = api

    def render(self, t):
        buf = ['digraph {']

        for s in map(lambda x: x['name'], self._api.sources(t)['sources']):
            outputs = self._api.source(t, s)['source']['status']['output_stats']['outputs']
            for out in outputs.keys():
                buf += ['{0} -> {1}'.format(s, out)]

        for s in map(lambda x: x['name'], self._api.streams(t)['streams']):
            outputs = self._api.stream(t, s)['stream']['status']['output_stats']['outputs']
            for out in outputs.keys():
                buf += ['{0} -> {1}'.format(s, out)]

        buf += ['}']

        return '\n'.join(buf)

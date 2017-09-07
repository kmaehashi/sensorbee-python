# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, print_function, unicode_literals

import time
from unittest import TestCase
from . import SB_TEST_HOST, SB_TEST_PORT

from pysensorbee.api import SensorBeeAPI, ResultSet, SensorBeeAPIError, WebSocketClient


class SensorBeeAPITest(TestCase):
    TOPOLOGY = 'test'
    TOPOLOGY2 = 'test2'

    def setUp(self):
        self.api = SensorBeeAPI(SB_TEST_HOST, SB_TEST_PORT)
        self.api.delete_topology(self.TOPOLOGY)
        self.api.create_topology(self.TOPOLOGY)

    def tearDown(self):
        self.api.delete_topology(self.TOPOLOGY)
        self.api.delete_topology(self.TOPOLOGY2)

    def test_init(self):
        self.assertEqual(SB_TEST_HOST, self.api.host)
        self.assertEqual(SB_TEST_PORT, self.api.port)

    def test_runtime_status(self):
        status = self.api.runtime_status()
        self.assertTrue(isinstance(status, dict))
        self.assertTrue('pid' in status)

    def test_topologies(self):
        api = self.api
        self.assertEqual(1, len(api.topologies()['topologies']))

        self.assertEqual(self.TOPOLOGY2,
            api.create_topology(self.TOPOLOGY2)['topology']['name'])
        try:
            self.assertEqual(2, len(api.topologies()['topologies']))
        finally:
            self.assertEqual({}, api.delete_topology(self.TOPOLOGY2))
            self.assertEqual(1, len(api.topologies()['topologies']))

    def test_sources(self):
        api = self.api
        self.assertEqual(0, api.sources(self.TOPOLOGY)['count'])
        api.query(self.TOPOLOGY,
            'CREATE SOURCE ns TYPE node_statuses;')
        try:
            self.assertEqual(1, api.sources(self.TOPOLOGY)['count'])
            self.assertEqual('ns',
                api.source(self.TOPOLOGY, 'ns')['source']['name'])
        finally:
            api.query(self.TOPOLOGY,
                'DROP SOURCE ns;')

    def test_streams(self):
        api = self.api
        self.assertEqual(0, api.streams(self.TOPOLOGY)['count'])
        api.query(self.TOPOLOGY,
            'CREATE SOURCE ns TYPE node_statuses;'
            'CREATE STREAM s AS SELECT RSTREAM * FROM ns [RANGE 1 TUPLES];')
        try:
            self.assertEqual(1, api.streams(self.TOPOLOGY)['count'])
            self.assertEqual('s',
                api.stream(self.TOPOLOGY, 's')['stream']['name'])
        finally:
            api.query(self.TOPOLOGY,
                'DROP STREAM s;'
                'DROP SOURCE ns;')

    def test_sinks(self):
        api = self.api
        self.assertEqual(0, api.sinks(self.TOPOLOGY)['count'])
        api.query(self.TOPOLOGY,
            'CREATE SINK snk TYPE stdout;')
        try:
            self.assertEqual(1, api.sinks(self.TOPOLOGY)['count'])
            self.assertEqual('snk',
                api.sink(self.TOPOLOGY, 'snk')['sink']['name'])
        finally:
            api.query(self.TOPOLOGY,
                'DROP SINK snk;')

    def test_query(self):
        api = self.api
        result = api.query(self.TOPOLOGY,
            'EVAL 7 * 6;')
        self.assertEqual(42, result['result'])
        result = api.query(self.TOPOLOGY,
            'CREATE SOURCE ns TYPE node_statuses;')
        try:
            self.assertEqual('running', result['status'])
            result = api.query(self.TOPOLOGY, '''
                SELECT RSTREAM [LIMIT 2]
                    *,
                    "✓" AS test_unicode
                FROM ns [RANGE 1 TUPLES];''')
            self.assertTrue(isinstance(result, ResultSet))
            self.assertEqual(2, len(list(result)))
        finally:
            api.query(self.TOPOLOGY,
                'DROP SOURCE ns;')

    def test_error(self):
        self.assertRaises(SensorBeeAPIError, self.api.sources, 'no_such_topology')
        self.assertRaises(SensorBeeAPIError, self.api.query, self.TOPOLOGY, 'INVALID BQL')

    def test_wsquery(self):
        api = self.api
        wsc = api.wsquery(self.TOPOLOGY)
        wsc.start()
        try:
            wsc._test_done = False
            def callback(wsc2, rid, type, payload):
                self.assertEqual(wsc, wsc2)
                self.assertEqual(1, rid)
                self.assertEqual('result', type)
                self.assertEqual({'result': 42}, payload)
                wsc2._test_done = True
            wsc.send('EVAL 7 * 6;', callback, 1)
            while not wsc._test_done:
                time.sleep(0.1)
        finally:
            wsc.close()

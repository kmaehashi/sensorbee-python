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

    def test_error(self):
        self.assertRaises(SensorBeeAPIError, self.api.sources, 'no_such_topology')
        self.assertRaises(SensorBeeAPIError, self.api.query, self.TOPOLOGY, 'INVALID BQL')

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
            self.assertEqual(self.TOPOLOGY2, api.topology(self.TOPOLOGY2)['topology']['name'])
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

    def test_wsquery(self):
        api = self.api
        api.query(self.TOPOLOGY, 'CREATE SOURCE ns TYPE node_statuses WITH interval = 0.1;')
        wsc = api.wsquery(self.TOPOLOGY)
        wsc.start()
        try:
            # One-shot
            wsc._test_oneshot = False
            def callback_1(wsc2, rid, type, payload):
                self.assertEqual(wsc, wsc2)
                self.assertEqual(1, rid)
                self.assertEqual('result', type)
                self.assertEqual({'result': 42}, payload)
                wsc._test_oneshot = True
            wsc.send('EVAL 7 * 6;', callback_1, 1)

            # Stream
            wsc._test_stream = False
            wsc._test_stream_types = []
            def callback_2(wsc2, rid, type, payload):
                self.assertEqual(2, rid)
                if type == 'eos':
                    self.assertEqual(['sos', 'result', 'result'], wsc._test_stream_types)
                    wsc._test_stream = True
                wsc._test_stream_types.append(type)
            wsc.send('SELECT RSTREAM [LIMIT 2] * FROM ns [RANGE 1 TUPLES];', callback_2, 2)

            # Error
            wsc._test_error = False
            def callback_3(wsc2, rid, type, payload):
                self.assertEqual(3, rid)
                self.assertEqual('error', type)
                wsc._test_error = True
            wsc.send('INVALID BQL', callback_3, 3)

            # Wait for above tests to complete.
            while not (wsc._test_oneshot and wsc._test_stream and wsc._test_error):
                time.sleep(0.1)

            # Request ID in use
            wsc._test_stream2 = False
            def callback_4(wsc2, rid, type, payload):
                if type == 'eos':
                    wsc._test_stream2 = True
            wsc.send('SELECT RSTREAM [LIMIT 100] * FROM ns [RANGE 1 TUPLES];', callback_4, 4)
            self.assertRaises(RuntimeError, wsc.send, 'EVAL 0;', callback_4, 4)

            # Wait for above tests to complete.
            while not (wsc._test_stream2):
                time.sleep(0.1)

            # Now the request ID can be reused.
            wsc.send('EVAL 0;', callback_4, 4)

            # Exception in callback
            def callback_5(wsc2, rid, type, payload):
                print("--- this test prints a stack trace; ignore it. ---")
                raise RuntimeError('expected exception')
            wsc.send('EVAL 0;', callback_5, 5)

            # Wait for the above tests to complete.
            while not wsc.get_error():
                time.sleep(0.1)

            self.assertEqual('expected exception', wsc.get_error().args[0])
        finally:
            wsc.close()

# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, print_function, unicode_literals

import time
from unittest import TestCase
from . import SB_TEST_HOST, SB_TEST_PORT

from pysensorbee.api import SensorBeeAPI
from pysensorbee.cli import SbStatCommand, SbPeekCommand


class SbStatCommandTest(TestCase):
    TOPOLOGY = 'cli_test'

    def setUp(self):
        self.api = SensorBeeAPI(SB_TEST_HOST, SB_TEST_PORT)
        self.api.delete_topology(self.TOPOLOGY)
        self.api.create_topology(self.TOPOLOGY)
        self.api.query(self.TOPOLOGY,
            'CREATE SOURCE ns TYPE node_statuses;')

        self.cmd = SbStatCommand()
        self.args = [
            '--host', SB_TEST_HOST,
            '--port', SB_TEST_PORT,
        ]

    def tearDown(self):
        self.api.delete_topology(self.TOPOLOGY)

    def test_main(self):
        self.assertEqual(0, self.cmd.main(self.args))
        self.assertEqual(0, self.cmd.main(self.args + ['--json']))
        self.assertEqual(0, self.cmd.main(self.args + ['--dot']))

class SbPeekCommandTest(TestCase):
    TOPOLOGY = 'cli_test'

    def setUp(self):
        self.api = SensorBeeAPI(SB_TEST_HOST, SB_TEST_PORT)
        self.api.delete_topology(self.TOPOLOGY)
        self.api.create_topology(self.TOPOLOGY)
        self.api.query(self.TOPOLOGY,
            'CREATE SOURCE ns TYPE node_statuses;')

        self.cmd = SbPeekCommand()
        self.args = [
            '--host', SB_TEST_HOST,
            '--port', SB_TEST_PORT,
            '--topology', self.TOPOLOGY,
            'ns',
        ]

    def tearDown(self):
        self.api.delete_topology(self.TOPOLOGY)

    def test_main(self):
        self.assertEqual(0, self.cmd.main(self.args))
        self.assertEqual(0, self.cmd.main(self.args + [
            '--count', '2',
            '--expressions', '*, "✔︎" AS unicode',
            '--oneline',
            '--omit-long-strings',
        ]))

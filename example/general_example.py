#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, print_function, unicode_literals

import sensorbee.api

class GeneralExample(object):
    def main(self):
        api = sensorbee.api.SensorBeeAPI()
        print("Runtime Status:")
        print(api.runtime_status())

        print("Create Topology:")
        print(api.create_topology('beepy_test'))
        try:
            print("List Topologies:")
            print(api.topologies())

            print("Show Topology:")
            print(api.topology('beepy_test'))

            print("Send CREATE SOURCE Query:")
            print(api.query('beepy_test', 'CREATE SOURCE ns TYPE node_statuses;'))

            print("List Sources:")
            print(api.sources('beepy_test'))

            print("List Streams:")
            print(api.streams('beepy_test'))

            print("List Sinks:")
            print(api.sinks('beepy_test'))

            print("Send EVAL Query:")
            print(api.query('beepy_test', 'EVAL 1+2+3;'))

            print("Send SELECT Query:")
            rs = api.query('beepy_test', 'SELECT RSTREAM * FROM ns [RANGE 1 TUPLES];')
            count = 3
            for r in rs:
                print(r)
                count -= 1
                if count <= 0:
                    break

            print("Show Source:")
            print(api.source('beepy_test', 'ns'))
        finally:
            print("Delete Topology:")
            print(api.delete_topology('beepy_test'))

        print("List Topologies:")
        print(api.topologies())

if __name__ == '__main__':
    GeneralExample().main()

#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, print_function, unicode_literals

import sensorbee.api

class GeneralExample(object):
    def main(self):
        api = sensorbee.api.SensorBeeAPI()
        print(api.runtime_status())
        print(api.create_topology('beepy_test'))
        print(api.topologies())
        print(api.topology('beepy_test'))
        print(api.sources('beepy_test'))
        print(api.streams('beepy_test'))
        print(api.sinks('beepy_test'))
        print(api.query('beepy_test', 'EVAL 1+2+3;'))
        print(api.delete_topology('beepy_test'))
        print(api.topologies())

if __name__ == '__main__':
    GeneralExample().main()

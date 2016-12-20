#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
WebSocket Example

``pip install websocket-client`` to use websocket client API.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

import sensorbee.api
import time

#import websocket
#websocket.enableTrace(True)

class WebSocketExample(object):
    def main(self, topology='ws_test'):
        api = sensorbee.api.SensorBeeAPI()
        api.create_topology(topology)

        try:
            client = api.wsquery(topology)
            client.start()

            def callback(client, rid, type, msg):
                print("-------------------------------")
                print("RID: {0}".format(rid))
                print("Type: {0}".format(type))
                print("Message: {0}".format(msg))

            client.send("eval 1+2+3;", callback, 1)
            client.send("invalid_syntax", callback, 2)
            api.query(topology, "CREATE SOURCE node_stats TYPE node_statuses")  # sync
            client.send("SELECT RSTREAM * FROM node_stats [RANGE 1 TUPLES];", callback, 3)
            time.sleep(5)
        finally:
            api.delete_topology(topology)
            time.sleep(3)

if __name__ == '__main__':
    WebSocketExample().main()

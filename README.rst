|Travis|_ |Coveralls|_ |PyPi|_

.. |Travis| image:: https://api.travis-ci.org/kmaehashi/sensorbee-python.svg?branch=master
.. _Travis: https://travis-ci.org/kmaehashi/sensorbee-python

.. |Coveralls| image:: https://coveralls.io/repos/kmaehashi/sensorbee-python/badge.svg?branch=master&service=github
.. _Coveralls: https://coveralls.io/r/kmaehashi/sensorbee-python

.. |PyPi| image:: https://badge.fury.io/py/sensorbee-python.svg
.. _PyPi: https://badge.fury.io/py/sensorbee-python

sensorbee-python
================

This is a Python client library for `SensorBee <http://sensorbee.io/>`_ REST / WebSocket API.
This library also provides utility commands (``sbstat`` and ``sbpeek``) which can be used to inspect SensorBee topology.

Install
-------

::

  pip install sensorbee-python

To use WebSocket Client API, you also need to install `websocket-client <https://github.com/websocket-client/websocket-client>`_:

::

  pip install websocket-client

Requirements
------------

* Python 2.7, 3.3, 3.4, 3.5 or 3.6.

Usage
-----

Python API
~~~~~~~~~~

In most cases the only class you need to use is ``pysensorbee.api.SensorBeeAPI``.
Here is an example:

.. code-block:: python

  from pysensorbee import SensorBeeAPI

  api = SensorBeeAPI('127.0.0.1', 15601)
  api.create_topology('test')
  api.query('test', 'CREATE SOURCE ns TYPE node_statuses;')
  for r in api.query('test', 'SELECT RSTREAM * FROM ns [RANGE 1 TUPLES];'):
    print(r)

See ``pydoc pysensorbee.api`` for details.

Commands
~~~~~~~~

``sbstat`` provides a brief summary of the topology status.

::

  $ sbstat -H 127.0.0.1 -P 15601 -t test
     Node                          Status    Received   Error   Output                            Sent     Queued   Dropped
  -> node_stats                    running                      (total)                           5381                    0
                                                                    sensorbee_tmp_8               5381   0 (0.0%)
  :: sensorbee_tmp_8               running       5381       0   (total)                           5381                    0
                                                                    sensorbee_tmp_select_sink_7   5381   0 (0.0%)
  <- sensorbee_tmp_select_sink_7   running       5381       0

Sources, streams and sinks are indicated by ``->``, ``::`` and ``<-``, respectively.

``sbpeek`` can be used to peek what tuple is currently running through the specified source or stream.

::

  $ sbpeek -H 127.0.0.1 -P 15601 -t test -1 node_stats
  {"behaviors": {"remove_on_stop": false, "stop_on_disconnect": false}, "node_type": "source", "output_stats": {"num_sent_total": 5893, "outputs": {"sensorbee_tmp_58": {"queue_size": 1024, "num_sent": 0, "num_queued": 0}, "sensorbee_tmp_8": {"queue_size": 1024, "num_sent": 5893, "num_queued": 0}}, "num_dropped": 0}, "state": "running", "node_name": "node_stats"}

See ``sbstat --help`` and ``sbpeek --help`` for details.

Notice
------

* This library is not a part of the official SensorBee project.
* In addition to APIs documented in the `API Specification Version 1 <https://github.com/sensorbee/sensorbee/blob/master/server/v1_api.md>`_, this library supports some undocumented APIs, including WebSocket API.
* This project is a successor of `beepy <https://github.com/kmaehashi/beepy>`_.

License
-------

MIT License

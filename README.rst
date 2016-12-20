|Travis|_ |PyPi|_

.. |Travis| image:: https://api.travis-ci.org/kmaehashi/sensorbee-python.svg?branch=master
.. _Travis: https://travis-ci.org/kmaehashi/sensorbee-python

.. |PyPi| image:: https://badge.fury.io/py/sensorbee-python.svg
.. _PyPi: https://badge.fury.io/py/sensorbee-python

sensorbee-python
================

This is a Python client library for `SensorBee <http://sensorbee.io/>`_ REST / WebSocket API.
This library also provides ``sbstat`` command, which can be used to monitor SensorBee topology status.

Install
-------

::

  pip install sensorbee-python

To use WebSocket Client API, you also need to install `websocket-client <https://github.com/liris/websocket-client>`_:

::

  pip install websocket-client

Requirements
------------

* Python 2.6, 2.7, 3.3, 3.4 or 3.5.

Usage
-----

See ``sbstat --help`` for the usage.

Notice
------

* This library is not a part of the official SensorBee project.
* In addition to APIs documented in the `API Specification Version 1 <https://github.com/sensorbee/sensorbee/blob/master/server/v1_api.md>`_, this library supports some undocumented APIs, including WebSocket API.
* This project is a successor of `beepy <https://github.com/kmaehashi/beepy>`_.

License
-------

MIT License

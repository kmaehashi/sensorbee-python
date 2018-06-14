ChangeLog
=========

Release 0.3.2 (2018-06-14)
---------------------------------------

* Improvements
    * Drop support for Python 2.6
    * Add ``is_open`` API to WebSocketClient

Release 0.3.1 (2017-09-07)
---------------------------------------

* Improvements
    * Raise error when duplicate request ID is used in WebSocket API
    * Add unit tests

Release 0.3.0 (2017-09-01)
---------------------------------------

* Improvements
    * Add ``--expressions`` option to ``sbpeek``
    * Translate error object returned from SensorBee

Release 0.2.2 (2017-08-25)
---------------------------------------

* Improvements
    * Explicitly use UTF-8 to decode messages returned from SensorBee
    * Support Python 3.6

Release 0.2.1 (2017-05-01)
---------------------------------------

* Improvements
    * Improve ``sbstat`` to display runtime status
    * Add ``--omit-long-strings`` option to ``sbpeek``

Release 0.2.0 (2017-02-06)
---------------------------------------

* Improvements
    * Module name changed from ``sensorbee`` to ``pysensorbee`` to avoid conflict
    * Add ``--oneline`` option to ``sbpeek``
    * Improve ``sbpeek`` to uses SELECT RSTREAM LIMIT syntax
    * Other small refactorings

Release 0.1.2 (2016-12-25)
---------------------------------------

* New Features
    * Add ``sbpeek`` command

* Improvements
    * Improve synchronous query API to avoid using read buffer
    * Support specifying number of records to read in Peeker tool
    * Improve ``example/general_example.py``

Release 0.1.1 (2016-12-20)
---------------------------------------

* Bug Fixes
    * ``sbstat``: fix display order of nodes not sorted properly

Release 0.1.0 (2016-12-20)
---------------------------------------

Initial release.

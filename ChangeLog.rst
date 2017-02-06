ChangeLog
=========

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

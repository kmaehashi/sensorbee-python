# -*- coding: utf-8 -*-

import os

def _getenv(key):
    v = os.environ.get(key, None)
    if v is None:
        raise RuntimeError('environment variable {0} must be defined'.format(key))
    return v

SB_TEST_HOST = _getenv('SB_TEST_HOST')
SB_TEST_PORT = _getenv('SB_TEST_PORT')

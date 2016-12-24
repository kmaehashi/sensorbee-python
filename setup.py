#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup, find_packages

def _read(filename):
  with open(filename) as f:
    return f.read()

# Load package version.
exec(_read('sensorbee/_version.py'))

setup(name='sensorbee-python',
      version=__version__,
      description='SensorBee REST API Client',
      long_description=_read('README.rst'),
      url='https://github.com/kmaehashi/sensorbee-python',
      author='Kenichi Maehashi',
      author_email='webmaster@kenichimaehashi.com',
      license='MIT',
      classifiers=[
          'Programming Language :: Python',
          'Programming Language :: Python :: 2',
          'Programming Language :: Python :: 2.6',
          'Programming Language :: Python :: 2.7',
          'Programming Language :: Python :: 3',
          'Programming Language :: Python :: 3.3',
          'Programming Language :: Python :: 3.4',
          'Programming Language :: Python :: 3.5',
      ],
      packages=find_packages(exclude=['sensorbee.test']),
      test_suite = 'sensorbee.test',
      entry_points={
          'console_scripts': [
              'sbstat=sensorbee.cli:sbstat',
              'sbpeek=sensorbee.cli:sbpeek',
          ],
      },
      extras_require={
          'websocket': ['websocket-client'],
      },
)

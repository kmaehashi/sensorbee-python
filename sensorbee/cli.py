# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, print_function, unicode_literals

import sys
import json
import optparse

from .api import SensorBeeAPI
from .tools.spider import Spider
from .tools.dot import DotView
from .tools.top import TopView
from .tools.peeker import Peeker
from ._version import __version__

class _OptionParser(optparse.OptionParser, object):
    def __init__(self, *args, **kwargs):
        self._error = False
        super(_OptionParser, self).__init__(*args, **kwargs)

    def error(self, msg):
        self._msg = msg
        self._error = True

def print_out(out, msg):
    out.write(msg)

class SbStatCommand(object):
    def __init__(self, out=sys.stdout, err=sys.stderr):
        self._out = out
        self._err = err
        self._parser = self._create_parser()

    def main(self, argv):
        err = self._err
        (params, _) = self._parser.parse_args(argv + [''])  # [''] is added to workaround optparse bug

        # Failed to parse options.
        if self._parser._error:
            print_out(err, 'Error: {0}'.format(self._parser._msg))
            self.print_usage()
            return 2

        # Help option is specified.
        if params.help:
            self.print_usage()
            return 0

        # Validate parameters.
        if params.port < 1 or 65535 < params.port:
            print_out(err, 'Error: port number out of range: {0}\n'.format(params.port))
            self.print_usage()
            return 1
        if params.json and params.topology:
            print_out(err, 'Error: --json and --topology cannot be used at once\n')
            self.print_usage()
            return 1
        if params.json and params.dot:
            print_out(err, 'Error: --json and --dot cannot be used at once\n')
            self.print_usage()
            return 1

        api = SensorBeeAPI(params.host, params.port)

        if params.json:
            # Raw JSON mode
            json.dump(Spider(api).get(), self._out, indent=4)
            print_out(self._out, '\n')
            return 0

        # Determine which topology to use.
        topos = [t['name'] for t in api.topologies()['topologies']]
        if params.topology is None:
            if len(topos) == 1:
                print_out(err, 'Using topology: {0}\n'.format(topos[0]))
                params.topology = topos[0]
            elif len(topos) == 0:
                print_out(err, 'Error: No topology available on this SensorBee instance\n')
                return 1
            else:
                print_out(err, 'Error: --topology must be specified when multiple topologies are available\n')
                print_out(err, 'Topologies: {0}\n'.format(', '.join(topos)))
                return 1
        else:
            if params.topology not in topos:
                print_out(err, 'Error: topology {0} not found\n'.format(params.topology))
                print_out(err, 'Topologies: {0}\n'.format(', '.join(sorted(topos))))
                return 1

        if params.dot:
            # DOT mode
            print_out(self._out, DotView(api).render(params.topology))
            print_out(self._out, '\n')
        else:
            # Top mode (default)
            print_out(self._out, TopView(api).render(params.topology))
            print_out(self._out, '\n')

        return 0

    def _create_parser(self):
        version = '%prog {0}'.format(__version__)
        usage = 'Usage: %prog [options]'
        parser = _OptionParser(version=version, usage=usage, add_help_option=False)
        parser.add_option('-H', '--host', type='string', default='127.0.0.1',
                          help='host name or IP address of the server (default: %default)')
        parser.add_option('-P', '--port', type='int', default=15601,
                          help='port number of the server (default: %default)')
        parser.add_option('-t', '--topology', type='string', default=None,
                          help='topology name')
        parser.add_option('--json', default=False, action='store_true',
                          help='dump results as JSON')
        parser.add_option('--dot', default=False, action='store_true',
                          help='dump results as DOT')
        parser.add_option('--help', default=False, action='store_true',
                          help='print the usage and exit')
        return parser

    def print_usage(self):
        err = self._err
        print_out(err, '\n')
        print_out(err, 'sbstat - SensorBee Status Monitoring Tool\n')
        print_out(err, '\n')
        self._parser.print_help(err)
        print_out(err, '\n')

class SbPeekCommand(object):
    def __init__(self, out=sys.stdout, err=sys.stderr):
        self._out = out
        self._err = err
        self._parser = self._create_parser()

    def main(self, argv):
        err = self._err
        (params, streams) = self._parser.parse_args(argv)

        # Failed to parse options.
        if self._parser._error:
            print_out(err, 'Error: {0}'.format(self._parser._msg))
            self.print_usage()
            return 2

        # Help option is specified.
        if params.help:
            self.print_usage()
            return 0

        # Validate parameters.
        if params.port < 1 or 65535 < params.port:
            print_out(err, 'Error: port number out of range: {0}\n'.format(params.port))
            self.print_usage()
            return 1
        if len(streams) == 0:
            print_out(err, 'Error: stream name must be specified\n')
            self.print_usage()
            return 1
        if 1 < len(streams):
            print_out(err, 'Error: only one stream name can be specified\n')
            self.print_usage()
            return 1

        api = SensorBeeAPI(params.host, params.port)
        stream = streams[0]

        # Determine which topology to use.
        topos = [t['name'] for t in api.topologies()['topologies']]
        if params.topology is None:
            if len(topos) == 1:
                print_out(err, 'Using topology: {0}\n'.format(topos[0]))
                params.topology = topos[0]
            elif len(topos) == 0:
                print_out(err, 'Error: No topology available on this SensorBee instance\n')
                return 1
            else:
                print_out(err, 'Error: --topology must be specified when multiple topologies are available\n')
                print_out(err, 'Topologies: {0}\n'.format(', '.join(topos)))
                return 1
        else:
            if params.topology not in topos:
                print_out(err, 'Error: topology {0} not found\n'.format(params.topology))
                print_out(err, 'Topologies: {0}\n'.format(', '.join(sorted(topos))))
                return 1

        for d in Peeker(api).peek(params.topology, stream, params.count):
            print_out(self._out, json.dumps(d, indent=4))
            print_out(self._out, '\n')
            self._out.flush()

        return 0

    def _create_parser(self):
        version = '%prog {0}'.format(__version__)
        usage = 'Usage: %prog [options] stream'
        parser = _OptionParser(version=version, usage=usage, add_help_option=False)
        parser.add_option('-H', '--host', type='string', default='127.0.0.1',
                          help='host name or IP address of the server (default: %default)')
        parser.add_option('-P', '--port', type='int', default=15601,
                          help='port number of the server (default: %default)')
        parser.add_option('-t', '--topology', type='string', default=None,
                          help='topology name')
        parser.add_option('-c', '--count', type='int', default=1,
                          help='number of records to peek, 0 for infinite (default: %default)')
        parser.add_option('--help', default=False, action='store_true',
                          help='print the usage and exit')
        return parser

    def print_usage(self):
        err = self._err
        print_out(err, '\n')
        print_out(err, 'sbpeek - SensorBee Stream Peeker\n')
        print_out(err, '\n')
        self._parser.print_help(err)
        print_out(err, '\n')

def sbstat():
    cmd = SbStatCommand()
    retval = cmd.main(sys.argv[1:])
    sys.exit(retval)

def sbpeek():
    cmd = SbPeekCommand()
    retval = cmd.main(sys.argv[1:])
    sys.exit(retval)

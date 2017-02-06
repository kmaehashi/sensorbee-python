# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, print_function, unicode_literals

import contextlib
import json
import email.parser
import threading
import time

try:
    # Python 3
    from urllib.request import urlopen, Request
except ImportError:
    # Python 2
    from urllib2 import urlopen, Request

try:
    import websocket
    _WEBSOCKET_AVAILABLE = True
except ImportError:
    _WEBSOCKET_AVAILABLE = False


class SensorBeeAPI(object):
    def __init__(self, host='127.0.0.1', port=15601):
        """
        SensorBee API client.
        """
        self.host = host
        self.port = port

    def _url(self, path, scheme='http'):
        return '{0}://{1}:{2}/api/v1/{3}'.format(scheme, self.host, self.port, path)

    def _req(self, path, data=None, method=None):
        if method is None:
            method = 'GET' if data is None else 'POST'
        req = Request(self._url(path), data=data)
        req.get_method = lambda: method
        return json.loads(urlopen(req).read().decode())

    def runtime_status(self):
        """
        Returns the runtime status of the SensorBee process.
        """
        return self._req('runtime_status')

    def topologies(self):
        """
        Returns the list of topologies.
        """
        return self._req('topologies')

    def topology(self, t):
        """
        Returns the status of the specified topology.
        """
        return self._req('topologies/{0}'.format(t))

    def create_topology(self, t):
        """
        Creates a new topology using the specified name.
        """
        return self._req('topologies', json.dumps({'name': t}).encode())

    def delete_topology(self, t):
        """
        Deletes the specified topology.
        """
        return self._req('topologies/{0}'.format(t), None, 'DELETE')

    def sources(self, t):
        """
        Returns the list of sources in the topology.
        """
        return self._req('topologies/{0}/sources'.format(t))

    def source(self, t, s):
        """
        Returns the status of the specified source.
        """
        return self._req('topologies/{0}/sources/{1}'.format(t, s))

    def streams(self, t):
        """
        Returns the list of streams in the topology.
        """
        return self._req('topologies/{0}/streams'.format(t))

    def stream(self, t, s):
        """
        Returns the status of the specified stream.
        """
        return self._req('topologies/{0}/streams/{1}'.format(t, s))

    def sinks(self, t):
        """
        Returns the list of sinks in the topology.
        """
        return self._req('topologies/{0}/sinks'.format(t))

    def sink(self, t, s):
        """
        Returns the status of the specified sink.
        """
        return self._req('topologies/{0}/sinks/{1}'.format(t, s))

    def query(self, t, q):
        """
        Runs synchronous query on the topology.
        For ``SELECT`` queries, a ``ResultSet`` instance is returned; you can
        iterate over it to retrieve tuples.
        For other kind of queries, a dict instance that contains the result of
        the query is returned.
        """
        close = True
        f = urlopen(self._url('topologies/{0}/queries'.format(t)), json.dumps({'queries': q}).encode())
        try:
            msg = _MessageWrapper(f.info())
            mimetype = msg.get_content_type()
            if mimetype == 'application/json':
                return json.loads(f.read().decode())
            elif mimetype == 'multipart/mixed':
                rs = ResultSet(f, msg.get_param('boundary'))
                close = False
                return rs
            else:
                raise RuntimeError('unexpected MIME type: {0}'.format(mimetype))
        finally:
            if close:
                f.close()

    def wsquery(self, t):
        """
        Returns a WebSocket API client (``WebSocketClient``) for the topology.
        """
        if not _WEBSOCKET_AVAILABLE:
            raise RuntimeError('websocket module is unavailable')
        return WebSocketClient(self._url('topologies/{0}/wsqueries'.format(t), 'ws'))

class WebSocketClient(object):
    def __init__(self, uri):
        """
        SensorBee WebSocket API client.
        By using WebSocket API, you can run asynchronous query on the topology.

        Before sending queries through WebSocket API, you need to run the client
        application thread.  It can be started by ``start`` method.  If you want
        to manage the thread or other low-level things by yourself, you can use
        ``run`` and ``setup`` methods instead.
        """
        self._uri = uri
        self._app = None
        self._open = False
        self._error = None
        self._callback = {}
        self.setup()

    def __del__(self):
        app = self._app
        if app is not None:
            app.close()

    def start(self, async=False):
        """
        Starts the client application thread.  When ``async`` is set to False,
        this method waits for the connection to be established.
        """
        t = threading.Thread(target=self.run)
        t.daemon = True
        t.start()
        if not async:
            while not self._open:
                if self._error is not None:
                    raise self._error
                time.sleep(0.01)  # 10 msec

    def send(self, queries, callback, rid):
        """
        Sends the queries.  ``callback`` must be a function that accepts
        4 arguments (the client instance, request ID, message type and
        message contents).  ``rid`` must be a unique request ID in int.
        """
        if not self._open:
            raise RuntimeError('not connected')
        data = json.dumps({'rid': int(rid), 'payload': {'queries': queries}}).encode()
        self._callback[rid] = callback
        self._app.send(data)

    def close(self, **kwargs):
        """
        Shuts the connection down.
        """
        self._app.close(**kwargs)

    def get_error(self):
        """
        Returns the last error occurred.
        """
        return self._error

    def setup(self, **kwargs):
        """
        ``setup`` is a low-level interface for users who need to configure
        WebSocketApp details.
        """
        self._app = websocket.WebSocketApp(
            self._uri,
            on_open=self._on_open,
            on_message=self._on_message,
            on_error=self._on_error,
            on_close=self._on_close,
            **kwargs
        )

    def run(self, **kwargs):
        """
        ``run`` is a low-level interface for users who want to manually manage
        the application thread.
        """
        self._app.run_forever(**kwargs)

    def _on_open(self, ws):
        self._open = True

    def _on_message(self, ws, data):
        msg = json.loads(data)
        (msgRid, msgType, msgPayload) = (msg['rid'], msg['type'], msg['payload'])
        cb = self._callback[msgRid]
        # TODO: remove callback function
        cb(self, msgRid, msgType, msgPayload)

    def _on_error(self, ws, err):
        self._error = err

    def _on_close(self, ws):
        self._open = False

class _MessageWrapper(object):
    def __init__(self, msg):
        """
        This class is needed just for Python 2/3 compatibility.
        """
        self.msg = msg

    def get_content_type(self, *args, **kwargs):
        if hasattr(self.msg, 'gettype'):
            return self.msg.gettype(*args, **kwargs)
        return self.msg.get_content_type(*args, **kwargs)

    def get_param(self, *args, **kwargs):
        if hasattr(self.msg, 'getparam'):
            return self.msg.getparam(*args, **kwargs)
        return self.msg.get_param(*args, **kwargs)

class ResultSet(object):
    def __init__(self, _f, _boundary):
        self._f = _f
        self._boundary = _boundary

    def __del__(self):
        f = self._f
        if f:
            f.close()

    def _rbufsize(self, f, size):
        f.fp._rbufsize = size

    def __iter__(self):
        with contextlib.closing(self._f) as f:
            parser = email.parser.FeedParser()
            while True:
                self._rbufsize(f, 1)
                line = f.readline()
                if not line: break
                if line.rstrip() == '--{0}'.format(self._boundary).encode():
                    line = f.readline()
                    while line.rstrip():
                        parser.feed(line.decode())
                        line = f.readline()
                    length = int(parser.close()['Content-Length'])
                    self._rbufsize(f, length)
                    yield json.loads(f.read(length).decode())
                    parser = email.parser.FeedParser()

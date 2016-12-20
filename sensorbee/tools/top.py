# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, print_function, unicode_literals

from .spider import Spider


class TopView(object):
    FLAGS = {'source': '->', 'box': '::', 'sink': '<-'}

    def __init__(self, api):
        self._api = api

    def render(self, t):
        # Get all status values.
        ts = Spider(self._api).get_topology_status(t)
        allstats = {}
        allstats.update(ts['sources'])
        allstats.update(ts['streams'])
        allstats.update(ts['sinks'])

        # Determine the order of nodes to display.
        names = self._ordered_names(allstats)

        # Generate a table of status values.
        columns  = ['', 'Node', 'Status', 'Received', 'Error', 'Output', 'Sent', 'Queued', 'Dropped']
        lines = [columns]
        for s in [allstats[n] for n in names]:
            lines += self._generate_status_lines(self.FLAGS[s['node_type']], s['name'], s['state'], s['status'])

        # Adjust the column size nicely.
        colsize = [0] * len(columns)
        for line in lines:
            for (i, v) in enumerate(line):
                colsize[i] = max(colsize[i], len(str(v)))
        fmt = ''.join([
            '{0:<3}',
            '{1:<' + str(colsize[1] + 3) + '}',
            '{2:<' + str(colsize[2] + 3) + '}',
            '{3:>' + str(colsize[3] + 0) + '}',
            '{4:>' + str(colsize[4] + 3) + '}   ',
            '{5:<' + str(colsize[5] + 3) + '}',
            '{6:>' + str(colsize[6] + 0) + '}',
            '{7:>' + str(colsize[7] + 3) + '}',
            '{8:>' + str(colsize[8] + 3) + '}',
        ])

        # Render the table.
        rendered = [fmt.format(*map(str, line)) for line in lines]

        return '\n'.join(rendered)

    def _generate_status_lines(self, flag, name, state, status):
        # Flag, Node, Status, Received, Error, Output, Sent, Queued, Dropped
        lines = [[''] * 9]
        lines[0][0:3] = (flag, name, state)
        if 'input_stats' in status:  # Stream or Sink
            s = status['input_stats']
            lines[0][3:5] = (s['num_received_total'], s['num_errors'])
        if 'output_stats' in status:  # Stream or Source
            s = status['output_stats']
            for k in sorted(s['outputs'].keys()):
                v = s['outputs'][k]
                queue = v['num_queued']
                ratio = queue / v['queue_size'] * 100
                line = [''] * 9
                line[5:8] = ('    {0}'.format(k), v['num_sent'], '{0} ({1:3.1f}%)'.format(queue, ratio))
                lines.append(line)
            lines[0][5:9] = ('(total)', s['num_sent_total'], '', s['num_dropped'])
        return lines

    def _ordered_names(self, stats):
        """
        Determine the order of sources/streams/sinks to display:

        1. Sources
        2. Connected Streams
        3. Dangling Streams
        4. Connected Sinks
        5. Dangling Sinks
        """
        sources = sorted([x for x in stats if stats[x]['node_type'] == 'source'])
        streams = sorted([x for x in stats if stats[x]['node_type'] == 'box'])
        sinks = sorted([x for x in stats if stats[x]['node_type'] == 'sink'])

        # List streams/sinks connected from sources.
        # They are not "dangling".
        connected = []
        targets = list(sources)
        while True:
            targets2 = []
            for t in targets:
                if t in sinks: continue
                outs = sorted([out for out in stats[t]['status']['output_stats']['outputs'].keys() if out not in connected])
                connected += outs
                targets2 += outs
            if len(targets2) == 0: break
            targets = targets2

        return \
            sources + \
            [s for s in connected if s in streams] + \
            [s for s in streams   if s not in connected] + \
            [s for s in connected if s in sinks] + \
            [s for s in sinks     if s not in connected]

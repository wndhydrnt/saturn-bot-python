# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

import queue
import unittest

from saturn_bot import controller, stdio
from saturn_bot.plugin.grpc_stdio_pb2 import StdioData


class StdioServicerTest(unittest.TestCase):
    def test_StreamStdio(self):
        q = queue.SimpleQueue()
        stdio_adapter = stdio.Adapter(channel=StdioData.STDOUT, q=q)
        grpc_controller = controller.Servicer()
        # Shut down immediately to avoid a deadlock.
        grpc_controller.Shutdown(None, None)

        stdio_servicer = stdio.Servicer(q=q, shutdown_ctrl=grpc_controller)
        stdio_adapter.write("test message")
        result = list(stdio_servicer.StreamStdio(None, None))
        self.assertEqual(1, len(result))
        entry = result[0]
        self.assertEqual(StdioData.STDOUT, entry.channel)
        self.assertEqual("test message".encode("utf-8"), entry.data)

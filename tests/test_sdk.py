# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

import os.path
import tempfile
import unittest
from typing import Mapping
from unittest.mock import Mock

from saturn_bot import Context, Plugin
from saturn_bot.plugin.grpc_controller_pb2_grpc import GRPCController
from saturn_bot.protocol.v1 import saturnbot_pb2
from saturn_bot.sdk import PluginService, _find_open_port, serve


class UnitTestPlugin(Plugin):
    name = "Unit Test"
    priority = 10

    def __init__(
        self,
        raise_on_pr_closed: bool = False,
        raise_on_pr_created: bool = False,
        raise_on_pr_merged: bool = False,
    ):
        self.raise_on_pr_closed = raise_on_pr_closed
        self.raise_on_pr_created = raise_on_pr_created
        self.raise_on_pr_merged = raise_on_pr_merged

        self.on_pr_closed_called = False
        self.on_pr_created_called = False
        self.on_pr_merged_called = False
        self.config_key: str = ""

    def apply(self, ctx: Context) -> None:
        with open("test.txt", "w+") as f:
            f.write("unit test")

    def filter(self, ctx: Context) -> bool:
        return True

    def init(self, config: Mapping[str, str]) -> None:
        self.config_key = config.get("config_key", "")

    def on_pr_closed(self, ctx: Context):
        if self.raise_on_pr_closed is True:
            raise RuntimeError("on_pr_closed failed")

        self.on_pr_closed_called = True

    def on_pr_created(self, ctx: Context):
        if self.raise_on_pr_created is True:
            raise RuntimeError("on_pr_created failed")

        self.on_pr_created_called = True

    def on_pr_merged(self, ctx: Context):
        if self.raise_on_pr_merged is True:
            raise RuntimeError("on_pr_merged failed")

        self.on_pr_merged_called = True


class TaskServiceTest(unittest.TestCase):
    def test_ExecuteActions(self):
        plugin = UnitTestPlugin()
        context = saturnbot_pb2.Context()
        with tempfile.TemporaryDirectory() as d:
            request = saturnbot_pb2.ExecuteActionsRequest(path=d, context=context)

            service = PluginService(p=plugin)
            response = service.ExecuteActions(request=request, context={})

            self.assertEqual("", response.error)
            with open(os.path.join(d, "test.txt")) as f:
                self.assertEqual("unit test", f.read())

    def test_ExecuteActions__exception(self):
        plugin = Mock(spec=Plugin)
        plugin.name = "Unit Test"
        plugin.apply.side_effect = RuntimeError("plugin failed")
        context = saturnbot_pb2.Context()
        with tempfile.TemporaryDirectory() as d:
            request = saturnbot_pb2.ExecuteActionsRequest(path=d, context=context)

            service = PluginService(plugin)
            response = service.ExecuteActions(request=request, context={})

            self.assertEqual("failed to execute actions: plugin failed", response.error)
            self.assertFalse(os.path.exists(os.path.join(d, "test.txt")))

    def test_ExecuteFilters(self):
        plugin = UnitTestPlugin()
        context = saturnbot_pb2.Context()
        request = saturnbot_pb2.ExecuteFiltersRequest(context=context)

        service = PluginService(plugin)
        response = service.ExecuteFilters(request=request, context={})

        self.assertEqual("", response.error)
        self.assertTrue(response.match)

    def test_ExecuteFilters__exception(self):
        plugin = Mock(spec=Plugin)
        plugin.name = "Unit Test"
        plugin.filter.side_effect = RuntimeError("task failed")
        context = saturnbot_pb2.Context()
        request = saturnbot_pb2.ExecuteFiltersRequest(context=context)

        service = PluginService(plugin)
        response = service.ExecuteFilters(request=request, context={})

        self.assertEqual("failed to execute filters: task failed", response.error)
        self.assertFalse(response.match)

    def test_GetPlugin(self):
        plugin = UnitTestPlugin()
        request = saturnbot_pb2.GetPluginRequest(config={"config_key": "config value"})

        service = PluginService(plugin)
        response = service.GetPlugin(request=request, context={})

        self.assertEqual("", response.error)
        self.assertEqual("Unit Test", response.name)
        self.assertEqual(10, response.priority)
        self.assertEqual("config value", plugin.config_key)

    def test_GetPlugin__exception(self):
        plugin = Mock(spec=Plugin)
        plugin.name = "Unit Test"
        plugin.init.side_effect = RuntimeError("plugin failed")
        request = saturnbot_pb2.GetPluginRequest(config={})

        service = PluginService(plugin)
        response = service.GetPlugin(request=request, context={})

        self.assertEqual(
            "plugin 'Unit Test' failed during initialization: plugin failed",
            response.error,
        )

    def test_OnPrClosed(self):
        plugin = UnitTestPlugin()
        context = saturnbot_pb2.Context()
        request = saturnbot_pb2.OnPrClosedRequest(context=context)

        service = PluginService(plugin)
        response = service.OnPrClosed(request=request, context={})

        self.assertEqual("", response.error)
        self.assertTrue(plugin.on_pr_closed_called)

    def test_OnPrClosed__exception(self):
        plugin = UnitTestPlugin(raise_on_pr_closed=True)
        context = saturnbot_pb2.Context()
        request = saturnbot_pb2.OnPrClosedRequest(context=context)

        service = PluginService(plugin)
        response = service.OnPrClosed(request=request, context={})

        self.assertEqual(
            "failed to execute OnPrClosed event: on_pr_closed failed", response.error
        )
        self.assertFalse(plugin.on_pr_closed_called)

    def test_OnPrCreated(self):
        plugin = UnitTestPlugin()
        context = saturnbot_pb2.Context()
        request = saturnbot_pb2.OnPrCreatedRequest(context=context)

        service = PluginService(plugin)
        response = service.OnPrCreated(request=request, context={})

        self.assertEqual("", response.error)
        self.assertTrue(plugin.on_pr_created_called)

    def test_OnPrCreated__exception(self):
        plugin = UnitTestPlugin(raise_on_pr_created=True)
        context = saturnbot_pb2.Context()
        request = saturnbot_pb2.OnPrCreatedRequest(context=context)

        service = PluginService(plugin)
        response = service.OnPrCreated(request=request, context={})

        self.assertEqual(
            "failed to execute OnPrCreated event: on_pr_created failed", response.error
        )
        self.assertFalse(plugin.on_pr_closed_called)

    def test_OnPrMerged(self):
        plugin = UnitTestPlugin()
        context = saturnbot_pb2.Context()
        request = saturnbot_pb2.OnPrMergedRequest(context=context)

        service = PluginService(plugin)
        response = service.OnPrMerged(request=request, context={})

        self.assertEqual("", response.error)
        self.assertTrue(plugin.on_pr_merged_called)

    def test_OnPrMerged__exception(self):
        plugin = UnitTestPlugin(raise_on_pr_merged=True)
        context = saturnbot_pb2.Context()
        request = saturnbot_pb2.OnPrMergedRequest(context=context)

        service = PluginService(plugin)
        response = service.OnPrMerged(request=request, context={})

        self.assertEqual(
            "failed to execute OnPrMerged event: on_pr_merged failed", response.error
        )
        self.assertFalse(plugin.on_pr_merged_called)


class ServeTest(unittest.TestCase):
    def test_serve(self):
        port = _find_open_port()
        plugin = UnitTestPlugin()
        grpc_controller = GRPCController()
        server = serve(port=port, shutdown=grpc_controller, plugin=plugin)
        server.stop(0)

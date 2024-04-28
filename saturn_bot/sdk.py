# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

import contextlib
import errno
import os
import random
import socket
import sys
import time
from concurrent import futures
from typing import Iterator, Mapping

import grpc
from grpc_health.v1 import health_pb2, health_pb2_grpc
from grpc_health.v1.health import HealthServicer

from saturn_bot import Context
from saturn_bot.plugin import grpc_controller_pb2_grpc
from saturn_bot.protocol.v1 import saturnbot_pb2, saturnbot_pb2_grpc

BIND_IP: str = "127.0.0.1"


class Plugin:
    name: str
    priority: int = 0

    def init(self, config: Mapping[str, str]) -> None:
        pass

    def apply(self, ctx: Context) -> None:
        return None

    def filter(self, ctx: Context) -> bool:
        return True

    def on_pr_closed(self, ctx: Context):
        pass

    def on_pr_created(self, ctx: Context):
        pass

    def on_pr_merged(self, ctx: Context):
        pass


@contextlib.contextmanager
def in_checkout_dir(d: str) -> Iterator[None]:
    current = os.getcwd()
    os.chdir(d)
    try:
        yield
    finally:
        os.chdir(current)


class PluginService(saturnbot_pb2_grpc.PluginServiceServicer):
    def __init__(self, p: Plugin):
        self._plugin = p

    def ExecuteActions(
        self, request: saturnbot_pb2.ExecuteActionsRequest, context
    ) -> saturnbot_pb2.ExecuteActionsResponse:
        try:
            with in_checkout_dir(request.path):
                self._plugin.apply(ctx=request.context)
        except Exception as e:
            return saturnbot_pb2.ExecuteActionsResponse(
                error=f"failed to execute actions: {e}"
            )

        return saturnbot_pb2.ExecuteActionsResponse(error=None)

    def ExecuteFilters(
        self, request: saturnbot_pb2.ExecuteFiltersRequest, context
    ) -> saturnbot_pb2.ExecuteFiltersResponse:
        try:
            result = self._plugin.filter(ctx=request.context)
            return saturnbot_pb2.ExecuteFiltersResponse(match=result, error=None)
        except Exception as e:
            return saturnbot_pb2.ExecuteFiltersResponse(
                match=False,
                error=f"failed to execute filters: {e}",
            )

    def GetPlugin(
        self, request: saturnbot_pb2.GetPluginRequest, context
    ) -> saturnbot_pb2.GetPluginResponse:
        try:
            self._plugin.init(config=request.config)
            return saturnbot_pb2.GetPluginResponse(
                name=self._plugin.name, priority=self._plugin.priority, error=None
            )
        except Exception as e:
            return saturnbot_pb2.GetPluginResponse(
                error=f"plugin '{self._plugin.name}' failed during initialization: {e}"
            )

    def OnPrClosed(
        self, request: saturnbot_pb2.OnPrClosedRequest, context
    ) -> saturnbot_pb2.OnPrClosedResponse:
        try:
            self._plugin.on_pr_closed(request.context)
            return saturnbot_pb2.OnPrClosedResponse(error=None)
        except Exception as e:
            return saturnbot_pb2.OnPrClosedResponse(
                error=f"failed to execute OnPrClosed event: {e}"
            )

    def OnPrCreated(
        self, request: saturnbot_pb2.OnPrCreatedRequest, context
    ) -> saturnbot_pb2.OnPrCreatedResponse:
        try:
            self._plugin.on_pr_created(request.context)
            return saturnbot_pb2.OnPrCreatedResponse(error=None)
        except Exception as e:
            return saturnbot_pb2.OnPrCreatedResponse(
                error=f"failed to execute OnPrCreated event: {e}"
            )

    def OnPrMerged(
        self, request: saturnbot_pb2.OnPrMergedRequest, context
    ) -> saturnbot_pb2.OnPrMergedResponse:
        try:
            self._plugin.on_pr_merged(request.context)
            return saturnbot_pb2.OnPrMergedResponse(error=None)
        except Exception as e:
            return saturnbot_pb2.OnPrMergedResponse(
                error=f"failed to execute OnPrMerged event: {e}"
            )


class GRPCController(grpc_controller_pb2_grpc.GRPCControllerServicer):
    def __init__(self):
        self.is_shut_down = False

    def Shutdown(self, request, context):
        self.is_shut_down = True


def serve(port: int, shutdown: GRPCController, plugin: Plugin):
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    server.add_insecure_port(f"{BIND_IP}:{port}")

    saturnbot_pb2_grpc.add_PluginServiceServicer_to_server(
        servicer=PluginService(plugin), server=server
    )

    grpc_controller_pb2_grpc.add_GRPCControllerServicer_to_server(
        servicer=shutdown, server=server
    )

    health = HealthServicer()
    health.set("plugin", health_pb2.HealthCheckResponse.ServingStatus.Value("SERVING"))
    health_pb2_grpc.add_HealthServicer_to_server(servicer=health, server=server)
    server.start()
    return server


def serve_plugin(plugin: Plugin) -> None:
    port = _find_open_port()
    grpc_controller = GRPCController()
    server = serve(port=port, shutdown=grpc_controller, plugin=plugin)
    print(f"1|1|tcp|{BIND_IP}:{port}|grpc")
    sys.stdout.flush()
    try:
        while True:
            time.sleep(0.1)
            if grpc_controller.is_shut_down is True:
                server.stop(0)
                sys.exit(0)
    except KeyboardInterrupt:
        server.stop(0)


def _find_open_port() -> int:
    while True:
        port = random.randrange(start=11000, stop=12000)
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            s.bind((BIND_IP, port))
            return port
        except socket.error as e:
            if e.errno != errno.EADDRINUSE:
                raise e
        finally:
            if s is not None:
                s.close()

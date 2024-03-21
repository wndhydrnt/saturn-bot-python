# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

import collections.abc
import contextlib
import errno
import json
import os
import random
import socket
import sys
import time
from concurrent import futures
from typing import Iterable, Iterator

import grpc
from grpc_health.v1 import health_pb2, health_pb2_grpc
from grpc_health.v1.health import HealthServicer

from saturn_sync.plugin import grpc_controller_pb2_grpc
from saturn_sync.protocol.v1 import saturnsync_pb2, saturnsync_pb2_grpc
from saturn_sync.task import Task

BIND_IP: str = "127.0.0.1"


class Config(collections.abc.Mapping):
    def __init__(self, data: dict[str, str]):
        self._data = data

    def __getitem__(self, item: str) -> str:
        item_lower = item.lower()
        return self._data.get(item_lower, "")

    def __iter__(self):
        return self._data.__iter__()

    def __len__(self):
        return self._data.__len__()


@contextlib.contextmanager
def in_checkout_dir(d: str) -> Iterator[None]:
    current = os.getcwd()
    os.chdir(d)
    try:
        yield
    finally:
        os.chdir(current)


class TaskService(saturnsync_pb2_grpc.TaskServiceServicer):
    def __init__(self, tasks: Iterable[Task]):
        self._tasks: dict[str, Task] = {}
        for t in tasks:
            self._tasks[t.name] = t

    def ExecuteActions(
        self, request: saturnsync_pb2.ExecuteActionsRequest, context
    ) -> saturnsync_pb2.ExecuteActionsResponse:
        try:
            with in_checkout_dir(request.path):
                task = self._tasks.get(request.task_name, None)
                if task is None:
                    return saturnsync_pb2.ExecuteActionsResponse(
                        error=f"unknown task {request.task_name}"
                    )

                task.apply(ctx=request.context)
        except Exception as e:
            return saturnsync_pb2.ExecuteActionsResponse(
                error=f"exception during apply of {request.task_name}: {e}"
            )

        return saturnsync_pb2.ExecuteActionsResponse(error=None)

    def ExecuteFilters(
        self, request: saturnsync_pb2.ExecuteFiltersRequest, context
    ) -> saturnsync_pb2.ExecuteFiltersResponse:
        try:
            task = self._tasks.get(request.task_name, None)
            if task is None:
                return saturnsync_pb2.ExecuteFiltersResponse(
                    match=False, error=f"unknown task {request.task_name}"
                )

            result = task.filter(ctx=request.context)
            return saturnsync_pb2.ExecuteFiltersResponse(match=result, error=None)
        except Exception as e:
            return saturnsync_pb2.ExecuteFiltersResponse(
                match=False,
                error=f"exception during filtering of {request.task_name}: {e}",
            )

    def ListTasks(
        self, request: saturnsync_pb2.ListTasksRequest, context
    ) -> saturnsync_pb2.ListTasksResponse:
        try:
            config = Config(data=json.loads(request.custom_config))
            proto_tasks: list[saturnsync_pb2.Task] = []
            for t in self._tasks.values():
                t.init(config)
                proto_tasks.append(_to_proto_task(t))

            return saturnsync_pb2.ListTasksResponse(tasks=proto_tasks)
        except Exception as e:
            return saturnsync_pb2.ListTasksResponse(error=f"cannot list tasks: {e}")

    def OnPrClosed(
        self, request: saturnsync_pb2.OnPrClosedRequest, context
    ) -> saturnsync_pb2.OnPrClosedResponse:
        try:
            task = self._tasks.get(request.task_name, None)
            if task is None:
                return saturnsync_pb2.OnPrClosedResponse(
                    error=f"unknown task {request.task_name}"
                )

            task.on_pr_closed(request.context)
            return saturnsync_pb2.OnPrClosedResponse(error=None)
        except Exception as e:
            return saturnsync_pb2.OnPrClosedResponse(
                error=f"exception during execution: {e}"
            )

    def OnPrCreated(
        self, request: saturnsync_pb2.OnPrCreatedRequest, context
    ) -> saturnsync_pb2.OnPrCreatedResponse:
        try:
            task = self._tasks.get(request.task_name, None)
            if task is None:
                return saturnsync_pb2.OnPrCreatedResponse(
                    error=f"unknown task {request.task_name}"
                )

            task.on_pr_created(request.context)
            return saturnsync_pb2.OnPrCreatedResponse(error=None)
        except Exception as e:
            return saturnsync_pb2.OnPrCreatedResponse(
                error=f"exception during execution: {e}"
            )

    def OnPrMerged(
        self, request: saturnsync_pb2.OnPrMergedRequest, context
    ) -> saturnsync_pb2.OnPrMergedResponse:
        try:
            task = self._tasks.get(request.task_name, None)
            if task is None:
                return saturnsync_pb2.OnPrMergedResponse(
                    error=f"unknown task {request.task_name}"
                )

            task.on_pr_merged(request.context)
            return saturnsync_pb2.OnPrMergedResponse(error=None)
        except Exception as e:
            return saturnsync_pb2.OnPrMergedResponse(
                error=f"exception during execution: {e}"
            )


class GRPCController(grpc_controller_pb2_grpc.GRPCControllerServicer):
    def __init__(self):
        self.is_shut_down = False

    def Shutdown(self, request, context):
        self.is_shut_down = True


def serve(port: int, shutdown: GRPCController, tasks: Iterable[Task]):
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    server.add_insecure_port(f"{BIND_IP}:{port}")

    saturnsync_pb2_grpc.add_TaskServiceServicer_to_server(
        servicer=TaskService(tasks), server=server
    )

    grpc_controller_pb2_grpc.add_GRPCControllerServicer_to_server(
        servicer=shutdown, server=server
    )

    health = HealthServicer()
    health.set("plugin", health_pb2.HealthCheckResponse.ServingStatus.Value("SERVING"))
    health_pb2_grpc.add_HealthServicer_to_server(servicer=health, server=server)
    server.start()
    return server


def register_task(*tasks: Task) -> None:
    port = _find_open_port()
    grpc_controller = GRPCController()
    server = serve(port=port, shutdown=grpc_controller, tasks=tasks)
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


def _to_proto_task(task: Task) -> saturnsync_pb2.Task:
    return saturnsync_pb2.Task(
        name=task.name,
        auto_merge=task.auto_merge,
        auto_merge_after_seconds=task.auto_merge_after_seconds,
        branch_name=task.branch_name,
        change_limit=task.change_limit,
        commit_message=task.commit_message,
        create_only=task.create_only,
        disabled=task.disabled,
        filters=task.filters,
        keep_branch_after_merge=task.keep_branch_after_merge,
        labels=task.labels,
        merge_once=task.merge_once,
        pr_body=task.pr_body,
        pr_title=task.pr_title,
    )

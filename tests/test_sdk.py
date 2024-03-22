# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

import os.path
import tempfile
import unittest
from typing import Mapping
from unittest.mock import Mock

from saturn_sync import Context
from saturn_sync.plugin.grpc_controller_pb2_grpc import GRPCController
from saturn_sync.protocol.v1 import saturnsync_pb2
from saturn_sync.sdk import TaskService, _find_open_port, serve
from saturn_sync.task import Task


class UnitTestTask(Task):
    name = "Unit Test"

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
        task = UnitTestTask()
        context = saturnsync_pb2.Context()
        with tempfile.TemporaryDirectory() as d:
            request = saturnsync_pb2.ExecuteActionsRequest(
                task_name="Unit Test", path=d, context=context
            )

            service = TaskService(tasks=[task])
            response = service.ExecuteActions(request=request, context={})

            self.assertEqual("", response.error)
            with open(os.path.join(d, "test.txt")) as f:
                self.assertEqual("unit test", f.read())

    def test_ExecuteActions__unknown_task(self):
        task = UnitTestTask()
        context = saturnsync_pb2.Context()
        with tempfile.TemporaryDirectory() as d:
            request = saturnsync_pb2.ExecuteActionsRequest(
                task_name="Other", path=d, context=context
            )

            service = TaskService(tasks=[task])
            response = service.ExecuteActions(request=request, context={})

            self.assertEqual("unknown task Other", response.error)
            self.assertFalse(os.path.exists(os.path.join(d, "test.txt")))

    def test_ExecuteActions__exception(self):
        task = Mock(spec=Task)
        task.name = "Unit Test"
        task.apply.side_effect = RuntimeError("task failed")
        context = saturnsync_pb2.Context()
        with tempfile.TemporaryDirectory() as d:
            request = saturnsync_pb2.ExecuteActionsRequest(
                task_name="Unit Test", path=d, context=context
            )

            service = TaskService(tasks=[task])
            response = service.ExecuteActions(request=request, context={})

            self.assertEqual(
                "exception during apply of Unit Test: task failed", response.error
            )
            self.assertFalse(os.path.exists(os.path.join(d, "test.txt")))

    def test_ExecuteFilters(self):
        task = UnitTestTask()
        context = saturnsync_pb2.Context()
        request = saturnsync_pb2.ExecuteFiltersRequest(
            task_name="Unit Test", context=context
        )

        service = TaskService(tasks=[task])
        response = service.ExecuteFilters(request=request, context={})

        self.assertEqual("", response.error)
        self.assertTrue(response.match)

    def test_ExecuteFilters__unknown_task(self):
        task = UnitTestTask()
        context = saturnsync_pb2.Context()
        request = saturnsync_pb2.ExecuteFiltersRequest(
            task_name="Other", context=context
        )

        service = TaskService(tasks=[task])
        response = service.ExecuteFilters(request=request, context={})

        self.assertEqual("unknown task Other", response.error)
        self.assertFalse(response.match)

    def test_ExecuteFilters__exception(self):
        task = Mock(spec=Task)
        task.name = "Unit Test"
        task.filter.side_effect = RuntimeError("task failed")
        context = saturnsync_pb2.Context()
        request = saturnsync_pb2.ExecuteFiltersRequest(
            task_name="Unit Test", context=context
        )

        service = TaskService(tasks=[task])
        response = service.ExecuteFilters(request=request, context={})

        self.assertEqual(
            "exception during filtering of Unit Test: task failed", response.error
        )
        self.assertFalse(response.match)

    def test_ListTasks(self):
        task = UnitTestTask()
        request = saturnsync_pb2.ListTasksRequest(
            custom_config='{"config_key":"config value"}'.encode("utf-8")
        )

        service = TaskService(tasks=[task])
        response = service.ListTasks(request=request, context={})

        self.assertEqual("", response.error)
        task_want = saturnsync_pb2.Task(
            name="Unit Test",
            auto_merge=False,
            auto_merge_after_seconds=0,
            branch_name="",
            commit_message="",
            create_only=False,
            disabled=False,
            keep_branch_after_merge=False,
            merge_once=False,
            pr_body="",
            pr_title="",
        )
        self.assertEqual([task_want], response.tasks)
        self.assertEqual("config value", task.config_key)

    def test_ListTasks__exception(self):
        task = UnitTestTask()
        request = saturnsync_pb2.ListTasksRequest(custom_config="".encode("utf-8"))

        service = TaskService(tasks=[task])
        response = service.ListTasks(request=request, context={})

        self.assertEqual(
            "cannot list tasks: Expecting value: line 1 column 1 (char 0)",
            response.error,
        )

    def test_OnPrClosed(self):
        task = UnitTestTask()
        context = saturnsync_pb2.Context()
        request = saturnsync_pb2.OnPrClosedRequest(
            task_name="Unit Test", context=context
        )

        service = TaskService(tasks=[task])
        response = service.OnPrClosed(request=request, context={})

        self.assertEqual("", response.error)
        self.assertTrue(task.on_pr_closed_called)

    def test_OnPrClosed__unknown_task(self):
        task = UnitTestTask()
        context = saturnsync_pb2.Context()
        request = saturnsync_pb2.OnPrClosedRequest(task_name="Other", context=context)

        service = TaskService(tasks=[task])
        response = service.OnPrClosed(request=request, context={})

        self.assertEqual("unknown task Other", response.error)
        self.assertFalse(task.on_pr_closed_called)

    def test_OnPrClosed__exception(self):
        task = UnitTestTask(raise_on_pr_closed=True)
        context = saturnsync_pb2.Context()
        request = saturnsync_pb2.OnPrClosedRequest(
            task_name="Unit Test", context=context
        )

        service = TaskService(tasks=[task])
        response = service.OnPrClosed(request=request, context={})

        self.assertEqual(
            "exception during execution: on_pr_closed failed", response.error
        )
        self.assertFalse(task.on_pr_closed_called)

    def test_OnPrCreated(self):
        task = UnitTestTask()
        context = saturnsync_pb2.Context()
        request = saturnsync_pb2.OnPrCreatedRequest(
            task_name="Unit Test", context=context
        )

        service = TaskService(tasks=[task])
        response = service.OnPrCreated(request=request, context={})

        self.assertEqual("", response.error)
        self.assertTrue(task.on_pr_created_called)

    def test_OnPrCreated__unknown_task(self):
        task = UnitTestTask()
        context = saturnsync_pb2.Context()
        request = saturnsync_pb2.OnPrCreatedRequest(task_name="Other", context=context)

        service = TaskService(tasks=[task])
        response = service.OnPrCreated(request=request, context={})

        self.assertEqual("unknown task Other", response.error)
        self.assertFalse(task.on_pr_created_called)

    def test_OnPrCreated__exception(self):
        task = UnitTestTask(raise_on_pr_created=True)
        context = saturnsync_pb2.Context()
        request = saturnsync_pb2.OnPrCreatedRequest(
            task_name="Unit Test", context=context
        )

        service = TaskService(tasks=[task])
        response = service.OnPrCreated(request=request, context={})

        self.assertEqual(
            "exception during execution: on_pr_created failed", response.error
        )
        self.assertFalse(task.on_pr_closed_called)

    def test_OnPrMerged(self):
        task = UnitTestTask()
        context = saturnsync_pb2.Context()
        request = saturnsync_pb2.OnPrMergedRequest(
            task_name="Unit Test", context=context
        )

        service = TaskService(tasks=[task])
        response = service.OnPrMerged(request=request, context={})

        self.assertEqual("", response.error)
        self.assertTrue(task.on_pr_merged_called)

    def test_OnPrMerged__unknown_task(self):
        task = UnitTestTask()
        context = saturnsync_pb2.Context()
        request = saturnsync_pb2.OnPrMergedRequest(task_name="Other", context=context)

        service = TaskService(tasks=[task])
        response = service.OnPrMerged(request=request, context={})

        self.assertEqual("unknown task Other", response.error)
        self.assertFalse(task.on_pr_merged_called)

    def test_OnPrMerged__exception(self):
        task = UnitTestTask(raise_on_pr_merged=True)
        context = saturnsync_pb2.Context()
        request = saturnsync_pb2.OnPrMergedRequest(
            task_name="Unit Test", context=context
        )

        service = TaskService(tasks=[task])
        response = service.OnPrMerged(request=request, context={})

        self.assertEqual(
            "exception during execution: on_pr_merged failed", response.error
        )
        self.assertFalse(task.on_pr_merged_called)


class ServeTest(unittest.TestCase):
    def test_serve(self):
        port = _find_open_port()
        task = UnitTestTask()
        grpc_controller = GRPCController()
        server = serve(port=port, shutdown=grpc_controller, tasks=[task])
        server.stop(0)

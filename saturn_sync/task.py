# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

from typing import Mapping, Optional

from saturn_sync.protocol.v1.saturnsync_pb2 import Context, Filters


class Task:
    name: str
    auto_merge: bool = False
    auto_merge_after_seconds: int = 0
    branch_name: str = ""
    change_limit: Optional[int] = None
    commit_message: str = ""
    create_only: bool = False
    disabled: bool = False
    filters: Filters = Filters()
    keep_branch_after_merge: bool = False
    labels: list[str] = []
    merge_once: bool = False
    pr_body: str = ""
    pr_title: str = ""

    def init(self, config: Mapping[str, str]) -> None:
        pass

    def apply(self, ctx: Context) -> None:
        raise NotImplementedError("Task does not implement method apply()")

    def filter(self, ctx: Context) -> bool:
        raise NotImplementedError("Task does not implement method filter()")

    def on_pr_closed(self, ctx: Context):
        pass

    def on_pr_created(self, ctx: Context):
        pass

    def on_pr_merged(self, ctx: Context):
        pass

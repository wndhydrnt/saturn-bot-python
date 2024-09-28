# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

import os.path
import sys
import tempfile
from typing import Mapping, Optional

from saturn_bot import Context, Plugin, serve_plugin


class IntegrationTest(Plugin):
    name = "integration-test"

    def __init__(self) -> None:
        self.event_out_tmp_file_path: Optional[str] = None
        self.static_content: str = ""

    def apply(self, ctx: Context) -> None:
        if ctx.repository.full_name == "git.localhost/integration/log":
            # Writes to stdout
            print("Integration Test")
            # Writes to stderr
            print("Integration Test", file=sys.stderr)
            return

        with open("integration-test.txt", "w") as f:
            f.write(self.static_content)
            f.write("\n")
            f.write(ctx.run_data["dynamic"])

    def init(self, config: Mapping[str, str]) -> None:
        self.static_content = config["content"]
        if "event_out_tmp_file_path" in config:
            self.event_out_tmp_file_path = os.path.join(
                tempfile.gettempdir(), config["event_out_tmp_file_path"]
            )

    def filter(self, ctx: Context) -> bool:
        if ctx.repository.full_name == "git.localhost/integration/test":
            return True

        if ctx.repository.full_name == "git.localhost/integration/rundata":
            ctx.run_data["plugin"] = "set by plugin"
            return True

        return False

    def on_pr_closed(self, ctx: Context) -> None:
        if (
            self.event_out_tmp_file_path is None
            or ctx.repository.full_name != "git.localhost/integration/test"
        ):
            return

        with open(self.event_out_tmp_file_path, "w") as f:
            f.write("Integration Test OnPrClosed")

    def on_pr_created(self, ctx: Context) -> None:
        if (
            self.event_out_tmp_file_path is None
            or ctx.repository.full_name != "git.localhost/integration/test"
        ):
            return

        with open(self.event_out_tmp_file_path, "w") as f:
            f.write("Integration Test OnPrCreated")

    def on_pr_merged(self, ctx: Context) -> None:
        if (
            self.event_out_tmp_file_path is None
            or ctx.repository.full_name != "git.localhost/integration/test"
        ):
            return

        with open(self.event_out_tmp_file_path, "w") as f:
            f.write("Integration Test OnPrMerged")


if __name__ == "__main__":
    serve_plugin(IntegrationTest())

# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

from typing import Mapping

from saturn_bot import Context, Plugin, serve_plugin


class Example(Plugin):
    message: str

    def init(self, config: Mapping[str, str]) -> None:
        self.message = config["message"]

    def filter(self, ctx: Context) -> bool:
        # Match a single repository.
        # Implement more complex matching logic here by calling APIs.
        return ctx.repository.full_name == "github.com/wndhydrnt/saturn-bot-example"

    def apply(self, ctx: Context) -> None:
        # Create a file in the root of the repository.
        with open("hello-python.txt", "w+") as f:
            f.write(f"{self.message}\n")


if __name__ == "__main__":
    # Initialize and serve the plugin.
    serve_plugin(Example())

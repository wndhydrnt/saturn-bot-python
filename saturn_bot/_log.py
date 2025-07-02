# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

import logging


class _Formatter(logging.Formatter):
    def formatMessage(self, record: logging.LogRecord) -> str:
        if record.levelno == logging.CRITICAL or record.levelno == logging.ERROR:
            level = "error"
        elif record.levelno == logging.WARNING:
            level = "warn"
        elif record.levelno == logging.INFO:
            level = "info"
        else:
            level = "debug"

        return f"{level}%|%{record.getMessage()}"

    def usesTime(self):
        return False


def _configure_logging() -> None:
    rl = logging.getLogger()
    ch = logging.StreamHandler()
    ch.setFormatter(_Formatter())
    rl.addHandler(ch)
    # Hard-code the debug level here to ensure everything gets sent to saturn-bot.
    # saturn-bot then takes care of filtering the messages.
    rl.setLevel(logging.DEBUG)

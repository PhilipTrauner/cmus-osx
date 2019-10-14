from pathlib import Path
from re import compile as re_compile
from sys import executable
from sys import modules
from typing import Dict

from .env import Default

STATUS_DISPLAY_PROGRAM_REGEX = re_compile(r"set status_display_program=(.*)")
RC_ENTRY_REGEX = re_compile(r"shell\s(.*)\s&")

INTERPRETER_PATH = Path(executable)
MODULE_BASE_PATH = Path(modules[__name__].__file__).parent

RESOURCE_PATH = MODULE_BASE_PATH / "resource"
PAYLOAD_PATH = MODULE_BASE_PATH / "payload"

APP_ICON_NAME = "icon.png"
RC_SCRIPT_NAME = "rc_entry.sh"
SDP_SCRIPT_NAME = "status_display_program.sh"

APP_ICON_PATH = RESOURCE_PATH / APP_ICON_NAME

RC_PATH = PAYLOAD_PATH / "media_keys.py"
# (s)tatus_(d)isplay_(p)rogram
SDP_PATH = PAYLOAD_PATH / "notify.py"

CMUS_OSX_FOLDER_NAME = "cmus-osx"
CONFIG_NAME = "cmus-osx.conf"

SCRIPTS: Dict[str, str] = {
    RC_SCRIPT_NAME: f"#!/bin/sh\n\n{str(INTERPRETER_PATH)} {str(RC_PATH)}",
    SDP_SCRIPT_NAME: f'#!/bin/sh\n\n{str(INTERPRETER_PATH)} {str(SDP_PATH)} "${{@}}"',
}

COULD_NOT_LOCATED_CMUS_DIRECTORY = 1

ENV_VAR_PREFIX = "CMUS_OSX"
ENV: Dict[str, Default] = {
    "NOTIFICATION_ON_PAUSE": Default(
        False,
        validator=lambda value: type(value) is bool,
        hint="Controls if a notification should be display on pause",
    ),
    "ITUNES_STYLE_NOTIFICATION": Default(
        True,
        validator=lambda value: type(value) is bool,
        hint="Display album artwork as app icon instead of notification badge",
    ),
    "APP_ICON": Default(
        APP_ICON_PATH,
        validator=lambda value: value.expanduser().is_file(),
        transformer=lambda value: Path(value),
        hint="Fallback icon if album artwork extraction fails",
    ),
    "THROTTLE_INTERVAL": Default(
        0.0,
        validator=lambda value: value >= 0,
        hint="Throttle interval (adjust if experiencing duplicated key-pressses)",
    ),
}

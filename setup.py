#!/usr/bin/env python3
import argparse
from os import chdir
from os import environ
from os import listdir
from os.path import expanduser
from os.path import isdir
from os.path import isfile
from shutil import copy
from shutil import copytree
from shutil import rmtree
from subprocess import call
from subprocess import check_call
from sys import argv
from sys import executable
from tempfile import mkdtemp

REPO = "https://github.com/PhilipTrauner/cmus-osx.git"
BRANCH = "master"
FOLDER_NAME = "cmus-osx/"
COPY_FILES = ["requirements.txt", "setup.py"]
MISSING_DEP_HELP = "Consult the installation section in README."

if environ.get("ENV") is None:
    REQUIREMENTS_FILE = "requirements.txt"
elif environ.get("ENV") == "dev":
    REQUIREMENTS_FILE = "requirements-dev.txt"

CMUS_BASE_DIR = None
for cmus_base_dir in [expanduser("~/.config/cmus/"), expanduser("~/.cmus/")]:
    if isdir(cmus_base_dir):
        CMUS_BASE_DIR = cmus_base_dir

RC_PATH = CMUS_BASE_DIR + "rc"
MEDIA_KEYS_PATH = CMUS_BASE_DIR + FOLDER_NAME + "media-keys.py"
RC_ENTRY = "shell %s &\n" % MEDIA_KEYS_PATH
NOTIFY_PATH = CMUS_BASE_DIR + FOLDER_NAME + "notify.py"
AUTOSAVE_ENTRY = "set status_display_program=%s" % NOTIFY_PATH


def print_header():
    if CMUS_BASE_DIR is None:
        print("cmus config directory not found, aborting...")
        exit(1)
    else:
        print("cmus config directory: '%s'" % CMUS_BASE_DIR)


def process_reqs(action):
    pip_args = []
    if args.quiet is True:
        pip_args += ["-q"]

    if action == "install":
        print("Installing requirements...")
        check_call(
            [executable, "-m", "pip", "install", "-r", REQUIREMENTS_FILE] + pip_args
        )
    elif action == "uninstall":
        print("Uninstalling requirements...")
        check_call(
            [executable, "-m", "pip", "uninstall", "-r", REQUIREMENTS_FILE] + pip_args
        )


def install():
    print_header()
    process_reqs(argv[1])

    if isdir(CMUS_BASE_DIR):
        if isdir(CMUS_BASE_DIR + FOLDER_NAME):
            if args.no_replace is False:
                rmtree(CMUS_BASE_DIR + FOLDER_NAME)
                copytree(FOLDER_NAME, CMUS_BASE_DIR + FOLDER_NAME)
            else:
                src_files = listdir(FOLDER_NAME)
                for file in src_files:
                    copy(FOLDER_NAME + file, CMUS_BASE_DIR + FOLDER_NAME)
                rmtree(CMUS_BASE_DIR + FOLDER_NAME + "__pycache__", ignore_errors=True)

            for file in COPY_FILES:
                copy(file, CMUS_BASE_DIR + FOLDER_NAME + file)

    if isfile(RC_PATH):
        if RC_ENTRY not in open(RC_PATH, "r").read():
            open(RC_PATH, "a").write(RC_ENTRY)
    else:
        open(RC_PATH, "w+").write(RC_ENTRY)

    try:
        import mutagen  # noqa: F401
    except ImportError:
        print("mutagen not installed. %s" % MISSING_DEP_HELP)

    pyobjc_installed = False
    try:
        import AppKit  # noqa: F401
        import Foundation  # noqa: F401
        import Quartz  # noqa: F401
        import PyObjCTools  # noqa: F401

        pyobjc_installed = True
    except ImportError:
        print("pyobjc not installed. %s" % MISSING_DEP_HELP)
    if pyobjc_installed:
        call([NOTIFY_PATH, "title", "Install successful!"])

    if args.no_replace is False:
        print(
            "\nInstalled. To enable notifications execute:\n%s\nin cmus."
            % AUTOSAVE_ENTRY
        )


def uninstall():
    print_header()
    process_reqs(argv[1])

    if isdir(CMUS_BASE_DIR + FOLDER_NAME):
        rmtree(CMUS_BASE_DIR + FOLDER_NAME)
    if isfile(RC_PATH):
        rc_content = open(RC_PATH, "r").read().split("\n")
        if rc_content[-1] == "":
            rc_content = rc_content[:-1]
        rc = open(RC_PATH, "w")
        for line in rc_content:
            if line != RC_ENTRY.rstrip("\n"):
                rc.write(line + "\n")


def upgrade():
    tmpdir = mkdtemp()

    try:
        check_call(["git", "clone", "-b", BRANCH, REPO, tmpdir])
        print()
        chdir(tmpdir)
        check_call(["./setup.py", "install", "-q", "--no-replace"])
        print("Upgraded sucessfully")
    finally:
        rmtree(tmpdir)


parser = argparse.ArgumentParser()
commands = parser.add_subparsers(title="commands")

install_parser = commands.add_parser("install")
install_parser.set_defaults(func=install)
install_parser.add_argument("--quiet", "-q", default=False, action="store_true")
install_parser.add_argument("--no-replace", default=False, action="store_true")

uninstall_parser = commands.add_parser("uninstall")
uninstall_parser.set_defaults(func=uninstall)
upgrade_parser = commands.add_parser("upgrade")
upgrade_parser.set_defaults(func=upgrade)

args = parser.parse_args()

if len(argv) <= 1:
    parser.print_help()
else:
    args.func()

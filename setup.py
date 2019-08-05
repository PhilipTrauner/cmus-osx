#!/usr/bin/env python3
from os.path import expanduser
from os.path import isdir
from os.path import isfile
from shutil import copytree
from shutil import rmtree
from subprocess import call
from sys import argv
from sys import executable
from subprocess import check_output
from os import environ

FOLDER_NAME = "cmus-osx/"
MISSING_DEP_HELP = "Consult the installation section in README."

if environ.get('ENV') is None:
    REQUIREMENTS_FILE = "requirements.txt"
elif environ.get('ENV') == "dev":
    REQUIREMENTS_FILE = "requirements-dev.txt"

CMUS_BASE_DIR = None

for cmus_base_dir in [expanduser("~/.config/cmus/"), expanduser("~/.cmus/")]:
    if isdir(cmus_base_dir):
        CMUS_BASE_DIR = cmus_base_dir

if CMUS_BASE_DIR is None:
    print("cmus config directory not found, aborting...")
    exit(1)
else:
    print("cmus config directory: '%s'" % CMUS_BASE_DIR)


RC_PATH = CMUS_BASE_DIR + "rc"
MEDIA_KEYS_PATH = CMUS_BASE_DIR + FOLDER_NAME + "media-keys.py"
RC_ENTRY = "shell %s &\n" % MEDIA_KEYS_PATH
NOTIFY_PATH = CMUS_BASE_DIR + FOLDER_NAME + "notify.py"
AUTOSAVE_ENTRY = "set status_display_program=%s" % NOTIFY_PATH

def process_reqs(action):
    if action == "install":
        print("Installing requirements...")

        call([executable, '-m', 'pip', 'install', '-r', REQUIREMENTS_FILE])
    elif action == "uninstall":
        print("Uninstalling requirements...")
        call([executable, '-m', 'pip', 'uninstall', '-r', REQUIREMENTS_FILE])


def install():
    process_reqs(argv[1])

    if isdir(CMUS_BASE_DIR):
        if isdir(CMUS_BASE_DIR + FOLDER_NAME):
            rmtree(CMUS_BASE_DIR + FOLDER_NAME)
        copytree(FOLDER_NAME, CMUS_BASE_DIR + FOLDER_NAME)
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

    print("\nInstalled. To enable notifications execute:\n%s\nin cmus." % AUTOSAVE_ENTRY)


def uninstall():
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


COMMANDS = {"install": install, "uninstall": uninstall}

if len(argv) != 2:
    print("No action specified. (avaliable: %s)" % ", ".join(COMMANDS.keys()))
elif argv[1] in COMMANDS:
    COMMANDS[argv[1]]()

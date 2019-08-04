#!/usr/bin/env python3
import sys

status_raw = sys.argv[1:]
status = dict(zip(status_raw[0::2], status_raw[1::2]))

from os.path import isdir
from os.path import expanduser
from os.path import isfile
from os.path import dirname

from logging import basicConfig
from logging import error

LOG_FILENAME = "/tmp/cmus-osx-notify.log"
basicConfig(filename=LOG_FILENAME)


def exception_hook(exc_type, exc_value, exc_traceback):
    error("Uncaught exception", exc_info=(exc_type, exc_value, exc_traceback))


sys.excepthook = exception_hook

from meh import Config
from meh import Option
from meh import ExceptionInConfigError

CONFIG_PATH = None

for config_path in [
    expanduser("~/.config/cmus/cmus-osx/"),
    expanduser("~/.cmus/cmus-osx/"),
]:
    if isdir(config_path):
        CONFIG_PATH = config_path + "cmus-osx.config"


if CONFIG_PATH is None:
    raise Exception("cmus config directory not found, aborting...")


config = Config()
config += Option(
    "display_mode",
    2,
    validator=lambda x: x in (0, 1, 2),
    comment="0: Disables notifications; "
    "1: Keep old notifications around; "
    "2: Clear old notifications",
)
config += Option(
    "app_icon",
    dirname(CONFIG_PATH) + "/cmus-icon.png",
    comment="Fallback icon if no album artwork is avaliable",
)
config += Option(
    "notification_on_pause", False, comment="Also display notification on pause"
)
config += Option(
    "itunes_style_notification",
    True,
    comment="Display album artwork as app icon instead of notification badge",
)

try:
    config = config.load(CONFIG_PATH)
except (IOError, ExceptionInConfigError):
    config.dump(CONFIG_PATH)
    config = config.load(CONFIG_PATH)

if config.display_mode == 0:
    exit(0)

if config.app_icon:
    # expand the path in memory to avoid writing absolute paths to config file
    config._values["app_icon"] = expanduser(config.app_icon)
    if not isfile(config._values["app_icon"]):
        raise FileNotFoundError("invalid value for option 'app_icon'")

# Quickly exit if paused
if "status" in status:
    if not config.notification_on_pause:
        if status["status"] != "playing":
            exit(0)


from AppKit import NSData, NSImage, NSBitmapImageRep, NSMakeSize
from Foundation import NSUserNotificationCenter
from Foundation import NSUserNotification
from Quartz import CGImageGetWidth, CGImageGetHeight
from mutagen import File

cover = None

if "url" in status:
    status["status"] = "(streaming ...)"
    # the title may contain both the artist and the song name
    if "title" in status:
        title_pair = status["title"].split(" - ")
        if len(title_pair) > 1:
            status["artist"] = title_pair[0]
            status["title"] = title_pair[1]
    else:
        status["title"] = status["url"]
elif "file" in status and isfile(status["file"]):
    file = File(status["file"])
    # id3
    if "APIC:" in file:
        cover = file["APIC:"]
        cover = cover.data
    # mp4
    elif "covr" in file:
        covers = file["covr"]
        if len(covers) > 0:
            cover = covers[0]
    # flac
    elif file.pictures:
        cover = file.pictures[0].data

if config.notification_on_pause:
    title = "cmus %s" % status["status"]
else:
    title = "cmus"
subtitle = ""
message = ""

if "tracknumber" in status and status["tracknumber"].isnumeric():
    subtitle += "%s. " % status["tracknumber"]

if "title" in status:
    subtitle += status["title"]

if "artist" in status:
    message += status["artist"]

if "album" in status:
    message += " – %s" % status["album"]

if "date" in status and status["date"].isnumeric():
    message += " (%s)" % status["date"]


center = NSUserNotificationCenter.defaultUserNotificationCenter()
notification = NSUserNotification.alloc().init()

notification.setTitle_(title)
notification.setSubtitle_(subtitle)
notification.setInformativeText_(message)

if cover:  # the song has an embedded cover image
    data = NSData.alloc().initWithBytes_length_(cover, len(cover))
    image_rep = NSBitmapImageRep.alloc().initWithData_(data)
    size = NSMakeSize(CGImageGetWidth(image_rep), CGImageGetHeight(image_rep))
    image = NSImage.alloc().initWithSize_(size)
    image.addRepresentation_(image_rep)
    if config.itunes_style_notification:
        notification.setValue_forKey_(image, "_identityImage")
    else:
        notification.setValue_forKey_(
            NSImage.alloc().initByReferencingFile_(config.app_icon), "_identityImage"
        )
        notification.setContentImage_(image)
else:  # song has no cover image, show an icon
    notification.setValue_forKey_(
        NSImage.alloc().initByReferencingFile_(config.app_icon), "_identityImage"
    )

if config.display_mode == 1:
    notification.setIdentifier_("cmus")
elif config.display_mode == 2:
    center.removeAllDeliveredNotifications()

center.deliverNotification_(notification)

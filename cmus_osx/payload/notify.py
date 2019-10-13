import sys
from io import BytesIO
from os.path import isfile
from platform import mac_ver
from subprocess import call

from AppKit import NSBitmapImageRep
from AppKit import NSData
from AppKit import NSImage
from AppKit import NSMakeSize
from Foundation import NSUserNotification
from Foundation import NSUserNotificationCenter
from mutagen import File
from PIL import Image

from cmus_osx.constants import CMUS_OSX_FOLDER_NAME
from cmus_osx.constants import CONFIG_NAME
from cmus_osx.constants import ENV
from cmus_osx.constants import ENV_VAR_PREFIX
from cmus_osx.env import build_env
from cmus_osx.util import locate_cmus_base_path
from cmus_osx.util import source_env_file


def exception_hook(exc_type, exc_value, exc_traceback):
    call(["cmus-remote", "--raw", "echo cmus-osx error: %s" % str(exc_value)])


sys.excepthook = exception_hook

cmus_base_path = locate_cmus_base_path()

if cmus_base_path is not None:
    source_env_file(cmus_base_path / CMUS_OSX_FOLDER_NAME / CONFIG_NAME)

# Use defaults values if config file can't be located
env = build_env(ENV_VAR_PREFIX, ENV)

status_raw = sys.argv[1:]
status = dict(zip(status_raw[0::2], status_raw[1::2]))

# Quickly exit if paused
if "status" in status:
    if not env.notification_on_pause:
        if status["status"] != "playing":
            exit(0)

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
    elif hasattr(file, "pictures") and len(file.pictures) > 0:
        cover = file.pictures[0].data

if env.notification_on_pause:
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
elif "albumartist" in status:
    message += status["albumartist"]

if "album" in status:
    message += " – %s" % status["album"]

if "date" in status and status["date"].isnumeric():
    message += " (%s)" % status["date"]


center = NSUserNotificationCenter.defaultUserNotificationCenter()
notification = NSUserNotification.alloc().init()

notification.setTitle_(title)
notification.setSubtitle_(subtitle)
notification.setInformativeText_(message)

# To-Do: Data allocation currently doesn't work in Catalina
if mac_ver()[0] != "10.15":
    if cover is not None:  # the song has an embedded cover image
        data = NSData.alloc().initWithBytes_length_(cover, len(cover))
        image_rep = NSBitmapImageRep.alloc().initWithData_(data)

        # CGImageGetWidth started returning bogus values in macOS 10.14 ->
        # Use Pillow to extract the image dimensions
        size = NSMakeSize(*Image.open(BytesIO(cover)).size)

        image = NSImage.alloc().initWithSize_(size)
        image.addRepresentation_(image_rep)
        if env.itunes_style_notification:

            notification.setValue_forKey_(image, "_identityImage")
        else:
            notification.setValue_forKey_(
                NSImage.alloc().initByReferencingFile_(str(env.app_icon)),
                "_identityImage",
            )
            notification.setContentImage_(image)
    else:  # song has no cover image, show an icon
        notification.setValue_forKey_(
            NSImage.alloc().initByReferencingFile_(str(env.app_icon)), "_identityImage"
        )

center.removeAllDeliveredNotifications()

center.deliverNotification_(notification)

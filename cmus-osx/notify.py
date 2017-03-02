#!/usr/bin/env python3

from sys import argv

status_raw = argv[1:]
status = dict(zip(status_raw[0::2], status_raw[1::2]))


from sys import excepthook
from os.path import expanduser, isfile

import logging
LOG_FILENAME = "/tmp/cmus-osx-notify.log"
logging.basicConfig(filename=LOG_FILENAME)

def exception_hook(exc_type, exc_value, exc_traceback):
	logging.error("Uncaught exception", 
		exc_info=(exc_type, exc_value, exc_traceback))

excepthook = exception_hook

from Meh import Config, Option, ExceptionInConfigError

CONFIG_PATH = expanduser("~/.config/cmus/cmus-osx/cmus-osx.config")

config = Config()
config += Option("display_mode", 2, validator=lambda x: x in (0, 1, 2), 
	comment="0: Disables notifications; "
			"1: Keep old notifications around; "
			"2: Clear old notifications")
config += Option("app_icon", expanduser("~/.config/cmus/cmus-osx/cmus-icon.png"), 
	validator=isfile, comment="Fallback icon if no album artwork is avaliable")
config += Option("notification_on_pause", False, 
	comment="Also display notification on pause")
config += Option("itunes_style_notification", True, 
	comment="Display album artwork as app icon instead of notification badge")

try:
    config = config.load(CONFIG_PATH)
except (IOError, ExceptionInConfigError):
    config.dump(CONFIG_PATH)
    config = config.load(CONFIG_PATH)


if config.display_mode == 0:
	exit(0)

# Quickly exit if paused to preserve some battery
if "status" in status:
	if not config.notification_on_pause:
		if status["status"] != "playing":
			exit(0)


from AppKit import NSData, NSImage, NSBitmapImageRep, NSMakeSize
from Foundation import NSUserNotificationCenter
from Foundation import NSUserNotification
from Quartz import CGImageGetWidth, CGImageGetHeight
from mutagen import File


DEFAULT_STREAM_ICON = "/System/Library/CoreServices/CoreTypes.bundle/Contents/Resources/GenericNetworkIcon.icns"

cover = None

if "url" in status:
	if status["url"].startswith(('http://', 'https://')):
		cover = NSImage.alloc().initByReferencingFile_(DEFAULT_STREAM_ICON)
		status['status'] = status['status'] + " (streaming ...)"
		# the title may contain both the artist and the song name
		title_pair = status["title"].split(" - ")
		if len(title_pair) > 0:
			status["artist"] = title_pair[0]
			status["title"] = title_pair[1]

elif "file" in status:
	file = File(status["file"])
	# id3
	if 'APIC:' in file:
		cover = file['APIC:']
		cover = cover.data
	# mp4
	elif 'covr' in file:
		covers = file['covr']
		if len(covers) > 0:
			cover = covers[0]

if config.notification_on_pause:
	title = "cmus %s" % status["status"]
else:
	title = "cmus"
subtitle = ""
message = ""

if "tracknumber" in status and status["tracknumber"].isnumeric():
	subtitle += '%s. ' % status['tracknumber']

if "title" in status:
	subtitle += status["title"]

if "artist" in status:
	message += status["artist"]

if "album" in status:
	message += ' – %s' % status["album"]

if "date" in status and status["date"].isnumeric():
	message += " (%s)" % status["date"]


center = NSUserNotificationCenter.defaultUserNotificationCenter()
notification = NSUserNotification.alloc().init()

notification.setTitle_(title)
notification.setSubtitle_(subtitle)
notification.setInformativeText_(message)

if cover: # the song has an embedded cover image
	data = NSData.alloc().initWithBytes_length_(cover, len(cover))
	image_rep = NSBitmapImageRep.alloc().initWithData_(data)
	size = NSMakeSize(CGImageGetWidth(image_rep), 
		CGImageGetHeight(image_rep))
	image = NSImage.alloc().initWithSize_(size)
	image.addRepresentation_(image_rep)
	if config.itunes_style_notification:
		notification.setValue_forKey_(image, "_identityImage")
	else:
		notification.setValue_forKey_(
			NSImage.alloc().initByReferencingFile_(config.app_icon), "_identityImage")
		notification.setContentImage_(image)
else: # song has no cover image, show an icon
	notification.setValue_forKey_(
		NSImage.alloc().initByReferencingFile_(config.app_icon), "_identityImage")

if config.display_mode == 1:
	notification.setIdentifier_('cmus')
elif config.display_mode == 2:
	center.removeAllDeliveredNotifications()

center.deliverNotification_(notification)
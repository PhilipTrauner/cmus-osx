#!/usr/bin/env python3

from sys import argv

status_raw = argv[1:]
status = dict(zip(status_raw[0::2], status_raw[1::2]))

# Quickly exit if paused to preserve some battery
if "status" in status:
	if status["status"] != "playing":
		exit(0)

from sys import excepthook
from os.path import expanduser, isfile
import json

import logging
LOG_FILENAME = '/tmp/notify.log'
logging.basicConfig(filename=LOG_FILENAME)

def exception_hook(exc_type, exc_value, exc_traceback):
	logging.error("Uncaught exception", 
		exc_info=(exc_type, exc_value, exc_traceback))

excepthook = exception_hook

from AppKit import NSData, NSImage, NSBitmapImageRep, NSMakeSize
from Foundation import NSUserNotificationCenter
from Foundation import NSUserNotification
from Quartz import CGImageGetWidth, CGImageGetHeight
from mutagen import File

DISPLAY_MODE = 2
CONFIG_LOCATION = expanduser("~/.config/cmus/cmus-osx/config.json")
config_exists = False

def write_config(path):
	open(CONFIG_LOCATION, "w+").write(json.dumps({"display_mode" : 2}))

if isfile(CONFIG_LOCATION):
	try:
		config = json.loads(open(CONFIG_LOCATION, "r").read())
		config_exists = True
	except json.decoder.JSONDecodeError:
		write_config(CONFIG_LOCATION)
else:
	write_config(CONFIG_LOCATION)

if config_exists and "display_mode" in config:
	if config["display_mode"] in (1, 2, 3):
		DISPLAY_MODE = config["display_mode"]

# NSImage because CmusArguments.cover should always be an NSImage
DEFAULT_STREAM_ICON = '/System/Library/CoreServices/CoreTypes.bundle/Contents/Resources/GenericNetworkIcon.icns'
APP_ICON_PATH = expanduser("~/.config/cmus/cmus-osx/cmus-icon.png")

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
	notification.setValue_forKey_(image, "_identityImage")
else: # song has no cover image, show an icon
	notification.setValue_forKey_(
		NSImage.alloc().initByReferencingFile_(APP_ICON_PATH), "_identityImage")

if DISPLAY_MODE == 1:
	notification.setIdentifier_('cmus')
elif DISPLAY_MODE == 2:
	center.removeAllDeliveredNotifications()

center.deliverNotification_(notification)
#!/usr/bin/env python

import sys
import os
import json
import logging
logging.basicConfig(filename='/tmp/cmus-notify.log', filemode='w',
        level=logging.INFO)

try:
    from Foundation import NSUserNotification
    from Foundation import NSUserNotificationCenter
    import AppKit
except ImportError as e:
    log.critical('error: you need pyobjc package to use this feature.\n')
    raise e

try:
    from tinytag import TinyTag
    HAS_TINYTAG = True
except:
    HAS_TINYTAG = False
    pass

CMUS_OSX_CONFIG = os.path.expanduser('~/.config/cmus/cmus-osx.json')
UPDATE_OPTIONS_FROM_CONFIG = True

# default options may be over-written from cmus-osx.json file
#  if UPDATE_OPTIONS_FROM_CONFIG is true

# DISPLAY_MODE controls the notification verbosity
#  0 shows nothing, immediately quits
#  1 replace old notification with new one in notification center
#  2 clears old notifications, add new one
#  3 shows a new notification for each cmus status change
DISPLAY_MODE = 2

# the icon file path for notification, or set as '' to disable icon displaying
ALBUMART_PATH       = '/tmp/cmus-osx-cover.jpg'
DEFAULT_LOCAL_ICON  = '/System/Library/CoreServices/CoreTypes.bundle/Contents/Resources/Actions.icns'
DEFAULT_STREAM_ICON = '/System/Library/CoreServices/CoreTypes.bundle/Contents/Resources/GenericNetworkIcon.icns'


#------------------------------------------------------------------------------
class CmusArguments:
    def __init__(self, argv):
        self.title    = ''
        self.subtitle = ''
        self.message  = ''
        self.cover    = ''
        self.tags     = {
                'status': '',
                'artist': '',
                'album': '',
                'tracknumber': '',
                'title': '',
                'date': ''
                }

        argc = len(argv)
        if argc < 4:
            logging.critical('invalid arguments')
            sys.exit(1)

        d = dict(zip(argv[1::2], argv[2::2]))

        def copyTo(tag):
            if tag in d:
                self.tags[tag] = d[tag]

        copyTo('status')
        copyTo('artist')
        copyTo('album')
        copyTo('title')
        copyTo('tracknumber')
        copyTo('date')
        if 'file' in d: # local (also mounted) files
            self.__parse_file_path__(d['file'])
        elif 'url' in d: # streams
            self.__parse_file_path__(d['url'])

    def make(self):
        if self.tags['status']:
            def is_valid_int(v):
                try:
                    return True if int(v) > 0 else False
                except Exception:
                    return False;

            self.title = 'cmus {status}'.format(**self.tags)

            if is_valid_int(self.tags['tracknumber']):
                self.subtitle += '{tracknumber}) '.format(**self.tags)

            if self.tags['title']:
                self.subtitle += '{title}'.format(**self.tags)

            if self.tags['artist']:
                self.message += '{artist}'.format(**self.tags)

            if self.tags['album']:
                self.message += '\n{album}'.format(**self.tags)

            if is_valid_int(self.tags['date']):
                self.message += ' ({date})'.format(**self.tags)


    def __parse_file_path__(self, fpath):
        #chech if the file has been come from an steam
        if fpath.startswith(('http://', 'https://')):
            self.cover = DEFAULT_STREAM_ICON
            self.tags['status'] = self.tags['status'] + ' (streaming ...)'
            # the title may contain both the artist and the song name
            title = self.tags['title']
            i = title.find(' - ')
            if i > 0:
                self.tags['artist'] = title[:i]
                self.tags['title'] = title[i+3:]

            return;

        elif HAS_TINYTAG:
            try:
                tag = TinyTag.get(fpath, image=True)
                image_data = tag.get_image()
                if len(image_data) > 0:
                    with open(ALBUMART_PATH, 'w') as fpic:
                        fpic.write(image_data)
                        self.cover = ALBUMART_PATH
            except:
                pass


#------------------------------------------------------------------------------
class Notification:
    def __init__(self):
        pass

    def show(self, title, subtitle, message, cover):
        center = NSUserNotificationCenter.defaultUserNotificationCenter()
        notification = NSUserNotification.alloc().init()

        notification.setTitle_(title)
        notification.setSubtitle_(subtitle.decode('utf-8'))
        notification.setInformativeText_(message.decode('utf-8'))

        if cover: # the song has an embedded cover image
            img = AppKit.NSImage.alloc().initByReferencingFile_(cover)
            notification.setContentImage_(img)
        elif ALBUMART_PATH: # song has no cover image, show an icon
            img = AppKit.NSImage.alloc().initByReferencingFile_(DEFAULT_LOCAL_ICON)
            notification.setContentImage_(img)

        if DISPLAY_MODE == 1:
            notification.setIdentifier_('cmus')
        elif DISPLAY_MODE == 2:
            center.removeAllDeliveredNotifications()

        center.deliverNotification_(notification)


#------------------------------------------------------------------------------
class OptionLoader():
       def __init__(self):
           if UPDATE_OPTIONS_FROM_CONFIG is False:
               return # simply do nothing

           with open(CMUS_OSX_CONFIG, "r") as jfile:
               root = json.load(jfile)
               if 'notify' in root:
                   notify = root['notify']
                   if 'mode' in notify:
                       global DISPLAY_MODE
                       DISPLAY_MODE = notify['mode']

                   if 'icon_path' in notify:
                       global ALBUMART_PATH
                       ALBUMART_PATH = notify['icon_path']


#------------------------------------------------------------------------------
if __name__ == '__main__':
    OptionLoader()
    if DISPLAY_MODE == 0:
        sys.exit(1) # do nothing and quit

    try:
        cmus = CmusArguments(sys.argv)
        cmus.make()
        if cmus.title:
            noti = Notification()
            noti.show(cmus.title, cmus.subtitle, cmus.message, cmus.cover)
    except Exception:
        logging.exception("cmus nottify error!")


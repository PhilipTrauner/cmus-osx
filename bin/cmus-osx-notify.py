#!/usr/bin/python
import sys

from Foundation import NSUserNotification
from Foundation import NSUserNotificationCenter
import AppKit

display_mode = 1
#------------------------------------------------------------------------------
class CmusArguments:
    def __init__(self, argv):
        self.title    = ''
        self.subtitle = ''
        self.message  = ''
        self.tags     = {
                'status': '',
                'artist': '',
                'album': '',
                'track': '',
                'title': '',
                'date': ''
                }

        argc = len(argv)
        if argc < 4:
            print('invalid arguments')
            return

        n = 1
        while n < argc:
            arg = argv[n]

            if arg == 'status':
                n += 1
                self.tags['status'] = argv[n]
            elif arg == 'artist':
                n += 1
                self.tags['artist'] = argv[n]
            elif arg == 'album':
                n += 1
                self.tags['album'] = argv[n]
            elif arg == 'tracknumber':
                n += 1
                self.tags['track'] = argv[n]
            elif arg == 'title':
                n += 1
                self.tags['title'] = argv[n]
            elif arg == 'date':
                n += 1
                self.tags['date'] = argv[n]

            n += 1

    def make(self):
        if self.tags['status']:
            self.title = 'cmus {status}'.format(**self.tags)

            if self.tags['track']:
                self.subtitle += '{track}) '.format(**self.tags)

            if self.tags['title']:
                self.subtitle += '{title}'.format(**self.tags)

            if self.tags['artist']:
                self.message += '{artist}'.format(**self.tags)

            if self.tags['album']:
                self.message += '\n{album}'.format(**self.tags)

            if self.tags['date']:
                self.message += ' ({date})'.format(**self.tags)


#------------------------------------------------------------------------------
class Notification:
    def __init__(self):
        self.notification = NSUserNotification.alloc().init()

    def show(self, title, subtitle, message):
        center = NSUserNotificationCenter.defaultUserNotificationCenter()

        self.notification.setTitle_(title)
        self.notification.setSubtitle_(subtitle.decode('utf-8'))
        self.notification.setInformativeText_(message.decode('utf-8'))

        iconPath = '/System/Library/CoreServices/CoreTypes.bundle/Contents/Resources/Actions.icns'
        img = AppKit.NSImage.alloc().initByReferencingFile_(iconPath)
        self.notification.setContentImage_(img)

        if display_mode == 1:
            center.removeAllDeliveredNotifications()
        elif display_mode == 2:
            self.notification.setIdentifier_('cmus')

        center.deliverNotification_(self.notification)

#------------------------------------------------------------------------------
def main():
    if display_mode == 0:
        return

    cmus = CmusArguments(sys.argv)
    cmus.make()
    if cmus.title:
        noti = Notification()
        noti.show(cmus.title, cmus.subtitle, cmus.message)

if __name__ == '__main__':
    main()



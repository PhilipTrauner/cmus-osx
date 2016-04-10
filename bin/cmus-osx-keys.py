#!/usr/bin/python

import sys
import subprocess
import fcntl

# PyObjC-related imports
from AppKit import NSApplication, NSSystemDefined
from PyObjCTools import AppHelper

# constants
KEY_UP = 11
NSApplicationActivationPolicyProhibited = 2


class KeySocketApp(NSApplication):

    repeated = False

    def sendEvent_(self, event):
        if event.type() is NSSystemDefined and event.subtype() is 8:
            data      = event.data1()
            keyCode   = (data & 0xFFFF0000) >> 16
            keyFlags  = (data & 0x0000FFFF)
            keyState  = (keyFlags & 0xFF00) >> 8
            keyRepeat = keyFlags & 0x1

            if keyRepeat and keyState is not KEY_UP:
                if keyCode == 20:
                    self.repeated = True
                    subprocess.call(['cmus-remote', '-k', '-10'])
                elif keyCode == 19:
                    self.repeated = True
                    subprocess.call(['cmus-remote', '-k', '+10'])

            if keyState is KEY_UP:
                if self.repeated:
                    self.repeated = False
                elif keyCode == 20:
                    subprocess.call(['cmus-remote', '-r'])
                elif keyCode == 16:
                    subprocess.call(['cmus-remote', '-u'])
                elif keyCode == 19:
                    subprocess.call(['cmus-remote', '-n'])


#------------------------------------------------------------------------------
if __name__ == '__main__':
    # check for exclusive instance
    lock_file = open('/tmp/cmus-osx-keys.pid', 'w')
    try:
        fcntl.lockf(lock_file, fcntl.LOCK_EX | fcntl.LOCK_NB)
    except:
        print('another instance is already running')
        sys.exit(1)

    subprocess.call(['launchctl',
        'unload',
        '-w', '/System/Library/LaunchAgents/com.apple.rcd.plist'])

    # run osx app
    app = KeySocketApp.sharedApplication()
    app.setActivationPolicy_(NSApplicationActivationPolicyProhibited)
    AppHelper.runEventLoop()


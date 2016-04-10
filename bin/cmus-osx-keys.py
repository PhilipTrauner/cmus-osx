#!/usr/bin/python

import sys
import subprocess
# tendo provides application singleton
from tendo import singleton

# PyObjC-related imports
from AppKit import NSApplication, NSSystemDefined
from PyObjCTools import AppHelper

KEY_UP = 11

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
                    print "prev"
                    subprocess.call(['cmus-remote', '-k', '-10'])
                elif keyCode == 19:
                    self.repeated = True
                    print "forward"
                    subprocess.call(['cmus-remote', '-k', '+10'])

            if keyState is KEY_UP:
                if self.repeated:
                    self.repeated = False
                elif keyCode == 20:
                    print "PREV"
                    subprocess.call(['cmus-remote', '-r'])
                elif keyCode == 16:
                    print "PLAY"
                    subprocess.call(['cmus-remote', '-u'])
                elif keyCode == 19:
                    print "FORWARD"
                    subprocess.call(['cmus-remote', '-n'])

def runOSXapp():
    NSApplicationActivationPolicyProhibited = 2
    app = KeySocketApp.sharedApplication()
    app.setActivationPolicy_(NSApplicationActivationPolicyProhibited)
    AppHelper.runEventLoop()

if __name__ == '__main__':
    me = singleton.SingleInstance()
    subprocess.call(['launchctl',
        'unload',
        '-w', '/System/Library/LaunchAgents/com.apple.rcd.plist'])

    # run osx app in other thread
    runOSXapp()


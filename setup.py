#!/usr/bin/python

import os
import sys
import shutil
import platform
import re
from distutils.spawn import find_executable

#constants
INSTALL_PATH = '/usr/local/bin'
CMUS_SCRIPTS = ['cmus-osx.py', 'cmus-osx-keys.py', 'cmus-osx-notify.py']
CURR_PATH    = os.path.dirname(os.path.abspath(__file__))

CMUS_CONFIG  = os.path.expanduser('~/.config/cmus/autosave')
NOTIFY_APP   = os.path.join(INSTALL_PATH, 'cmus-osx-notify.py')
NOTIFY_KEY   = 'set status_display_program'

class Setup():

    def install(self):
        self.__check_dependecies()
        self.__copy_files()
        self.__link_cmus_config(True)

    def uninstall(self):
        self.__link_cmus_config(False)
        self.__remove_files()

    def __check_dependecies(self):
        if platform.system() != 'Darwin':
            print("error: this utility only works under OS X.\n  your platform does not need cmus-osx\n")
            sys.exit(1)
        else:
            v, _, p = platform.mac_ver()
            print("  verified: OS X {} / {}".format(v, p))

        cmus_path = find_executable('cmus')
        if cmus_path is None:
            print("error: cmus not found!\n  please first install cmus on OS X.\n")
            sys.exit(1)
        else:
            print("  verified: cmus path: {}".format(cmus_path))

        # check pyobjc
        try:
            from Foundation import NSUserNotification
            from AppKit import NSApplication
            from PyObjCTools import AppHelper
        except:
            print("error: to use this utility you need to install 'pyobjc' package first."
                    "\n  please just install it by `pip` or see the README.md for more information."
                    "\n  then simply reinstall `cmus-osx` again.");
            sys.exit(1)

        print("  verified: `pyobjc` has been found.\n")


    def __copy_files(self):
        if not os.path.exists(INSTALL_PATH):
            os.makedirs(INSTALL_PATH)

        for sf in CMUS_SCRIPTS:
            sf_path = os.path.join(INSTALL_PATH, sf)
            print('  copy to: {}'.format(sf_path))
            shutil.copy(os.path.join('./bin', sf), INSTALL_PATH)
            os.chmod(sf_path, 0755)

    def __remove_files(self):
        for sf in CMUS_SCRIPTS:
            sf_path = os.path.join(INSTALL_PATH, sf)
            if os.path.exists(sf_path):
                print('  removed: {}'.format(sf_path))
                os.remove(sf_path)

    def __link_cmus_config(self, add):
        if os.path.exists(CMUS_CONFIG):
            shutil.copy(CMUS_CONFIG, CMUS_CONFIG + '.bak') # make backup
            with open(CMUS_CONFIG, "wt") as fout:
                with open(CMUS_CONFIG + '.bak', "rt") as fin:
                    regex  = re.compile('^{}.*$'.format(NOTIFY_KEY))
                    newval = NOTIFY_APP if add else ''
                    for line in fin:
                        line = regex.sub('{}={}'.format(NOTIFY_KEY, newval), line)
                        fout.write(line)
                    print('  cmus configured: {} notification script'
                            .format('using' if add else 'stop using'))
        else:
            print('warning: {} not found, please configure notification script manually'
                    .format(CMUS_CONFIG))






#------------------------------------------------------------------------------
if __name__ == '__main__':
    s = Setup()
    cmd = 'install' if len(sys.argv) < 2 else sys.argv[1]

    if cmd == 'install' or cmd == '-i':
        s.install()

    elif cmd == 'uninstall' or cmd == '-u':
        s.uninstall()

    else:
        print("error: invalid argument.\n  $>./setup.py install\n  $>./setup.py uninstall")


#!/usr/bin/env python

import subprocess
import os
import signal
from distutils.spawn import find_executable

class Launcher():
    """a launcher class to control MacBook media key watcher and the cmus itself"""

    def start(self):
        """finds sub processes and executes them"""

        cmus_path = find_executable('cmus')
        if cmus_path is None:
            print('can not find cmus in your path, probably it\'s not installed yet')
            return # stop application

        python_path = find_executable('python')
        curr_dir    = os.path.dirname(os.path.abspath(__file__))
        key_path    = os.path.join(curr_dir, 'cmus-osx-keys.py')
        try: # cmus-osx-keys.py is optional
            self.proc_keys = subprocess.Popen(['/usr/bin/python', key_path])
        except:
            print('can not start macbook key watcher as: cmus-osx-keys.py')
            pass

        # cmus subprocess
        FNULL = open(os.devnull, 'w')
        # sink cmus errors and warnings to /dev/null
        self.proc_cmus = subprocess.Popen([cmus_path], stderr=FNULL)
        self.proc_cmus.communicate()


    def stop(self):
        """if has any subprocess, tries to kill them"""

        if hasattr(self, 'proc_keys') and self.proc_keys.pid:
            try:
                print('try to stop key watcher (pid={}) ...'.format(self.proc_keys.pid))
                self.proc_keys.terminate()
                subprocess.call(['launchctl', 'load',
                    '-w', '/System/Library/LaunchAgents/com.apple.rcd.plist'
                    ])
            except:
                pass

        if hasattr(self, 'proc_cmus') and self.proc_cmus:
            try:
                print('try to stop cmus (pid={}) ...'.format(self.proc_cmus.pid))
                self.proc_cmus.terminate()
            except:
                pass


    def __enter__(self):
        self.SIG = signal.SIGTERM
        self.org_handler = signal.getsignal(self.SIG)
        def handler(signum, frame):
            self.stop()
            signal.signal(self.SIG, self.org_handler)

        signal.signal(self.SIG, handler)
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.stop()


#------------------------------------------------------------------------------

if __name__ == '__main__':
    """launch application"""
    with Launcher() as app:
        app.start()

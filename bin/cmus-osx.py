#!/usr/bin/python

import subprocess
import os
import signal
from distutils.spawn import find_executable

class Launcher():
    """a launcher class to control MacBook media key watcher and the cmus itself"""

    def start(self):
        """finds sub processes and executes them"""

        python_path = find_executable('python')
        cmus_path   = find_executable('cmus')
        curr_dir    = os.path.dirname(os.path.abspath(__file__))
        key_path    = os.path.join(curr_dir, 'cmus-osx-keys.py')

        if cmus_path is None:
            print('can not find cmus in your path, probably it\'s not installed yet')
            return # stop application

        FNULL = open(os.devnull, 'w') # sink to null

        try: # cmus-osx-keys.py is optional
            self.proc_keys = subprocess.Popen([python_path, key_path],
                    stdout=FNULL, stderr=subprocess.STDOUT
                    )
        except:
            print('can not start macbook key watcher as: cmus-osx-keys.py')
            pass

        # cmus subprocess
        self.proc_cmus = subprocess.Popen([cmus_path],
                stderr=FNULL
                )
        self.proc_cmus.communicate()


    def stop(self):
        """if has any subprocess, tries to kill them"""

        if hasattr(self, 'proc_keys') and self.proc_keys.pid:
            try:
                print('try to kill key watcher (pid={}) ...'.format(self.proc_keys.pid))
                self.proc_keys.terminate()
            except:
                pass

        if hasattr(self, 'proc_cmus') and self.proc_cmus:
            try:
                print('try to kill cmus (pid={}) ...'.format(self.proc_cmus.pid))
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

def main():
    """launch application"""
    with Launcher() as app:
        app.start()

if __name__ == '__main__':
    main()

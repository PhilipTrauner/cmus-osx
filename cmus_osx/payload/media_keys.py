from os import _exit as exit
from subprocess import call
from subprocess import CalledProcessError
from subprocess import check_output
from threading import Thread
from time import sleep
from typing import List
from typing import Optional

from AppKit import NSApplication
from AppKit import NSApplicationActivationPolicyProhibited
from AppKit import NSKeyUp
from AppKit import NSSystemDefined
from PyObjCTools import AppHelper


class KeySocketApp(NSApplication):
    repeated = False

    def sendEvent_(self, event):
        if event.type() is NSSystemDefined and event.subtype() == 8:
            data = event.data1()
            key_code = (data & 0xFFFF0000) >> 16
            key_flags = data & 0x0000FFFF
            key_state = (key_flags & 0xFF00) >> 8
            key_repeat = key_flags & 0x1

        if key_repeat and key_state is not NSKeyUp:
            if key_code == 20:
                self.repeated = True
                call(["cmus-remote", "-k", "-10"])
            elif key_code == 19:
                self.repeated = True
                call(["cmus-remote", "-k", "+10"])

        if key_state is NSKeyUp:
            if self.repeated:
                self.repeated = False
        elif key_code in (20, 18):
            call(["cmus-remote", "-r"])
        elif key_code == 16:
            call(["cmus-remote", "-u"])
        elif key_code in (19, 17):
            call(["cmus-remote", "-n"])


class SingleInstanceChecker(Thread):
    def __init__(self):
        Thread.__init__(self)
        self.daemon = True
        self.running = False

    def run(self):
        self.running = True
        while self.running:
            cmus_instances = get_cmus_instances()
            if cmus_instances is not None:
                if len(cmus_instances) == 0:
                    exit(0)
                elif len(cmus_instances) > 1:
                    call(
                        [
                            "cmus-remote",
                            "--raw",
                            "echo Media key support disabled "
                            "because more than one cmus instance is running.",
                        ]
                    )
                    exit(1)
            else:
                call(
                    [
                        "cmus-remote",
                        "--raw",
                        "echo Media key support disabled because "
                        "enumerating cmus instances failed.",
                    ]
                )
                exit(1)
            sleep(1)

    def stop(self):
        self.running = False


def get_cmus_instances() -> Optional[List[int]]:
    try:
        return [
            int(pid)
            for pid in check_output(["pgrep", "-x", "cmus"]).decode().split("\n")
            if pid != ""
        ]
    except CalledProcessError:
        return None


cmus_instances = get_cmus_instances()
if cmus_instances is not None and len(cmus_instances) == 1:
    app = KeySocketApp.sharedApplication()
    app.setActivationPolicy_(NSApplicationActivationPolicyProhibited)
    single_instance_checker = SingleInstanceChecker()
    single_instance_checker.start()
    AppHelper.runEventLoop()
else:
    exit(1)

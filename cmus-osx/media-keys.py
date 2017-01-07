#!/usr/bin/env python3

from subprocess import check_output, call, CalledProcessError
from time import sleep
from AppKit import NSAlert, NSInformationalAlertStyle, NSApp, NSApplication
from AppKit import NSApplicationActivationPolicyProhibited, NSSystemDefined
from AppKit import NSKeyUp
from PyObjCTools import AppHelper
from threading import Thread
from os import _exit as exit

class KeySocketApp(NSApplication):
	repeated = False

	def sendEvent_(self, event):
		if event.type() is NSSystemDefined and event.subtype() is 8:
			data = event.data1()
			key_code = (data & 0xFFFF0000) >> 16
			key_flags = (data & 0x0000FFFF)
			key_state = (key_flags & 0xFF00) >> 8
			key_repeat = key_flags & 0x1


		if key_repeat and key_state is not NSKeyUp:
			if key_code == 20:
				self.repeated = True
				subprocess.call(['cmus-remote', '-k', '-10'])
			elif key_code == 19:
				self.repeated = True
				subprocess.call(['cmus-remote', '-k', '+10'])

		if key_state is NSKeyUp:
			if self.repeated:
				self.repeated = False
		elif key_code == 20 or key_code == 18:
			call(['cmus-remote', '-r'])
		elif key_code == 16:
			call(['cmus-remote', '-u'])
		elif key_code == 19 or key_code == 17:
			call(['cmus-remote', '-n'])

class SingleInstanceChecker(Thread):
	def __init__(self):
		Thread.__init__(self)
		self.daemon = True
		self.running = False

	def run(self):
		self.running = True
		while self.running:
			cmus_instances = get_cmus_instances()
			if len(cmus_instances) == 0:
				quit()
			if len(cmus_instances) > 1:
				call(["cmus-remote", "--raw", "echo Media key support disabled "
					"because more than one cmus instance is running."])
				quit(code=1)
			sleep(1)

	def stop(self):
		self.running = False		

def get_cmus_instances():
	pids = []
	try:
		pids = [int(pid) for pid in check_output(
			["pgrep", "-x", "cmus"]).decode().split("\n") if pid != ""]
	except CalledProcessError:
		pass
	return pids

def quit(code=0):
	call(['launchctl', 'load', '-w', 
		'/System/Library/LaunchAgents/com.apple.rcd.plist'])
	exit(code)


cmus_instances = get_cmus_instances()

if len(cmus_instances) == 1:
	call(['launchctl', 'unload', '-w', 
		'/System/Library/LaunchAgents/com.apple.rcd.plist'])
	app = KeySocketApp.sharedApplication()
	app.setActivationPolicy_(NSApplicationActivationPolicyProhibited)
	single_instance_checker = SingleInstanceChecker()
	single_instance_checker.start()
	AppHelper.runEventLoop()
else:
	quit(1)



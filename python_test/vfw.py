#!/usr/bin/python
from serialrouter import *
from init_tesbed3 import *
import fdpexpect
import time

TIMEOUT = 4
TIMEOUT_ERROR = "Timeout occurred."
EOF_ERROR = "Possible serial communication error. Please check that no other program is accessing the console port."

class Vfw(VM, serialrouter):
	def __init__(self, d, dsthost, port):
		self.loginprompt = "login:"
		self.initprompt = "#"
		self.cliprompt = "#"
		self.confprompt = "(config)#"
		self.username: N
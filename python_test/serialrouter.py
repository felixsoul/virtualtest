#!/usr/bin/python
import telnetlib
import time
import fdpexpect

print "Hello"

DEFAULTTIMEOUT = 8
SLEEPAFTERWRITE = 2
COMMANDSLOWNESS = 0.05

class RouterConfigurationException(Exception):
	pass

class SerialConnectedRouter(telnetlib.Telnet, fdpexpect.fdspawn):
	def __init__(self, dsthost, port, timeout=DEFAULTTIMEOUT):
		telnetlib.Telnet.__init__(dsthost, port)
		time.sleep(2)
		
		fdpexpect.fdspawn.__init__(self, self.fileno())
		self.maxread = 1

	def __del__(self):
		self.close()
		fdpexpect.fdspawn.__del__(self)

	def sendline(self, line):
		self.send(line + "\r\n")

	def sendcommand(self, command):
		print "Sending: %s" % command
		for c in command:
			self.send(c)
			time.sleep(SLEEPAFTERWRITE)
		self.sendline("")
		time.sleep(SLEEPAFTERWRITE)
		self.flush()
		self.flushOutput()

	def timedexpect(self, pattern, timeout = DEFAULTTIMEOUT, quiet = False):
		if not quiet:
			print "Expecting: %s" % pattern
		res = self.expect([pattern, fdpexpect.TIMEOUT], timeout=timeout)
		if res == 1:
			raise RouterConfigurationException("Timeout occurred.")

	def listexpect(self, patterns, timeout = DEFAULTTIMEOUT, quiet = False):
		res = self.expect(patterns, timeout = timeout)
		self.flushInput()
		if not quiet:
			print "Matched %s" % patterns[res]
		return res

	def readuntil(self, pattern, timeout = DEFAULTTIMEOUT):
		self.expect(pattern, timeout)
		return self.before
	

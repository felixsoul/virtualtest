#!/usr/bin/python
import os
TEXTWIDTH = 80
DESCFIELD = 0.6
SEPFIELD = 0.1
VALFIELD = 0.3

TEST_FAILED = 0
TEST_OK = 1
TEST_SKIPPED = 2

try:
	import curses
except:
	colorcodes = {
		"black": "",
		"red": "",
		"green": "",
		"yellow": "",
		"blue": "",
		"magenta": "",
		"cyan": "",
		"white": ""
	}
else:
	curses.setupterm()
	__ansifg = curses.tigetstr('setaf')
	colorcodes = {
		"black": curses.tparm(__ansifg, 0),
		"red": curses.tparm(__ansifg, 1),
		"green": curses.tparm(__ansifg, 2),
		"yellow": curses.tparm(__ansifg, 3),
		"blue": curses.tparm(__ansifg, 4),
		"magenta": curses.tparm(__ansifg, 5),
		"cyan": curses.tparm(__ansifg, 6),
		"white": curses.tparm(__ansifg, 7)
	}

import pickle
import time

class TestException(Exception):
	pass

class TestDependencyException(TestException):
	pass

class InvalidCommandException(TestException):
	pass

class Result():
	
	def __init__(self, description = "", value = None):
		self.description = description
		self.value = value

	def setValue(self, value):
		self.value = value

	def setDescription(self, description):
		self.description = description

	def getValue(self):
		return self.value

	def getDescription(self):
		return self.description

	def getDV(self):
		return (self.description, self.value)

	def __str__(self):
		descwidth = int(TEXTWIDTH*DESCFIELD)
		sepwidth = int(TEXTWIDTH*SEPFIELD)
		valwidth = int(TEXTWIDTH*VALFIELD)
		res = ""
		if isinstance(self.value, bool):
			if self.value:
				val = "Passed"
			else:
				val = "Failed"
		else:
			val = self.value
		res += "%*s" %(descwidth, self.description)
		res += " " * sepwidth
		res += "%-*s" %(valwidth,val)
		res += "\n"
		return res

	def getTeX(self):
		res = ""
		if isinstance(self.value, bool):
			if self.value:
				val = "Passed"
			else:
				val = "Failed"
		else:
			val = self.value
		res += "\t%s & %s \\\\\n" %(self.description, val)
		return res


class SubTest():
	def __init__(self, title, task = False):
		self.title = title
		self.results = list()
		self.finalresult = TEST_FAILED
		self.istask = task

	def addResult(self, description, result):
		newresult = Result(description, result)
		self.results.append(newresult)

	def setFinalResult(self, finalresult):
		self.finalresult = finalresult

	def getFinalResult(self):
		return self.finalresult

	def getFinalResultString(self):
		if self.istask:
			if self.finalresult == TEST_OK:
				return "DONE"
			elif self.finalresult == TEST_SKIPPED:
				return "SKIPPED"
			else:
				return "ERROR"
		else: 
			if self.finalresult == TEST_OK:
				return "PASSED"
			elif self.finalresult == TEST_SKIPPED:
				return "SKIPPED"
			else:
				return "FAILED"

	def getFinalResultColorString(self):
		res = ""
		if self.finalresult == TEST_OK:
			res += colorcodes["green"]
		else :
			res += colorcodes["red"]
		res += self.getFinalResultString()
		res += colorcodes["white"]
		return res

	def setTitle(self, title):
		self.title = title

	def getTitle(self):
		return self.title

	def __str__(self):
		descwidth = int(TEXTWIDTH*DESCFIELD)
		sepwidth = int(TEXTWIDTH*SEPFIELD)
		valwidth = int(TEXTWIDTH*VALFIELD)
		res = ""
		res += colorcodes["white"]
		res += "="*TEXTWIDTH
		res += "\n"
		res += colorcodes["yellow"]
		res += "%*s" %(descwidth, self.title)
		res += colorcodes["white"]
		res += " "*(sepwidth)
		res += "%-*s" %(valwidth, self.getFinalResultColorString())
		res += "\n"

		if self.results:
			res += "-"*TEXTWIDTH
			res += "\n"

		for result in self.results:
			res += str(result)

		return res

	def getTeX(self):
		val = self.getFinalResultString()
		res = ""
		res += "\t\\hline \n"
		res += "\t\\textbf{%s} & \\textbf{%s} \\\\\n" % (self.title, val)

		if self.results:
			res += "\t\\hline \n"

		for result in self.results:
			res += result.getTeX()

		return res

class Test():
	def __init__(self, test_title):
		self.title = test_title
		self.subtests = dict()
		self.currentindex = 0
		self.subtestorder = dict()
		self.dependencies = dict()

	def getTitle(self):
		return self.title

	def addSubtest(self, subtestlabel, task = False):
		newsubtest = SubTest(subtestlabel, task)
		self.subtests.update({subtestlabel: newsubtest})
		self.subtestorder.update({self.currentindex: subtestlabel})
		self.currentindex +=1

	def addSubtestDependency(self, subtestlabel, dependsonlabel):
		if not self.subtests.has_key(subtestlabel):
			errstr = "Invoke addSubtest() first"
			raise InvalidCommandException, errstr
		testdeps = self.dependencies.get(subtestlabel,[])
		testdeps.append(dependsonlabel)
		self.dependencies.update({subtestlabel: testdeps})

	def addSubtestTitle(self, subtestlabel, subtesttitle):
		if not self.subtests.has_key(subtestlabel):
			self.addSubtest(subtestlabel)
		self.subtests[subtestlabel].setTitle(subtesttitle)

	def printTitleString(self, outstring):
		print colorcodes["blue"], "-"*TEXTWIDTH
		print "\t", outstring
		print colorcodes["blue"], "-"*TEXTWIDTH, colorcodes["white"]

	def announce(self, outstring):
		print ""
		print colorcodes["yellow"], "\t", outstring, colorcodes["white"]
		print ""

	def begin(self, subtestlabel, failure_result_value = TEST_FAILED):
		if not self.subtests.has_key(subtestlabel):
			self.addSubtest(subtestlabel)
		self.subtests[subtestlabel].setFinalResult(failure_result_value)
		testdeps = self.dependencies.get(subtestlabel,[])

		for dep in testdeps:
			try: 
				dept = self.subtests[dep]
			except KeyError:
				errstr = "Test %s not found" %dep
				raise InvalidCommandException, errstr
			if dept.getFinalResult() != TEST_OK:
				outstring = "%sSkip: %s%s.%s" \
						% (colorcodes["yellow"], \
						colorcodes["magenta"],  \
						self.subtests[subtestlabel].getTitle(), \
						colorcodes["white"])
				self.printTitleString(outstring)
				errstr = "Dependencies not met for test %s." % subtestlabel
				raise TestDependencyException, errstr

		outstring = "%sBegin: %s%s, %s" % (colorcodes["yellow"], \
				colorcodes["magenta"], \
				self.subtests[subtestlabel].getTitle(), \
				colorcodes["white"])
		self.printTitleString(outstring)

	def addResult(self, subtestlabel, description, result):
		self.subtests[subtestlabel].addResult(description, result)

	def end(self, subtestlabel, finalresult = False):
		try:
			self.subtests[subtestlabel].setFinalResult(finalresult)
		except KeyError:
			errstr = "Test %s not found" % subtestlabel
			raise InvalidCommandException, errstr

		if finalresult == TEST_SKIPPED:
			return
		elif finalresult == TEST_OK:
			resstr = colorcodes["green"]
		else:
			resstr = colorcodes["red"]

		resstr += self.subtests[subtestlabel].getFinalResultString()
		resstr += colorcodes["white"]
		outstring = "%sFinish: %s%s, %s Result: %s%s" % (colorcodes["yellow"], \
					colorcodes["magenta"], \
					self.subtests[subtestlabel].getTitle(), \
					colorcodes["white"], \
					resstr, \
					colorcodes["white"])
		self.printTitleString(outstring)

	def __str__(self):
		title = ""
		title += "  " + colorcodes["white"]
		title += self.title
		title += "  " + colorcodes["blue"]
		res = ""
		res += colorcodes["blue"]
		res += "*" * TEXTWIDTH
		res += "\n"
		res += title.center( \
				TEXTWIDTH + \
				len(colorcodes["white"])+ \
				len(colorcodes["blue"]), \
				"*")
		res += "\n"
		res += "*" * TEXTWIDTH
		res += "\n"
		res += colorcodes["white"]
		orderkeys = self.subtestorder.keys()
		orderkeys.sort()
		for key in orderkeys:
			label = self.subtestorder[key]
			subtest = self.subtests[label]
			res += str(subtest)

		res += "=" * TEXTWIDTH
		res += "\n"
		res += colorcodes["blue"]
		res += "*" * TEXTWIDTH
		res += "\n"
		res += colorcodes["white"]
		return res

	def getTeX(self):
		title = self.title
		res = ""
		res += "\\begin{tabular}{|r|l|} \n"
		res += "\t\\hline \n"
		res += "\t\\multicolumn{2}{|c|}{%s} \\\\ \n" % title
		res += "\t\\hline \n"

		orderkeys = self.subtestorder.keys()
		orderkeys.sort()
		for key in orderkeys:
			label = self.subtestorder[key]
			subtest = self.subtests[label]
			res += subtest.getTeX()

		res += "\t\\hline \n"
		res += "\\end{tabular}"
		return res

	def save(self, filename = None, dir = None, quiet = False):
		if not filename:
			filename = self.getTitle() + "." + str(time.time())
		if not dir:
			dir = "."

		completefilename = dir + os.sep + filename

		try:
			outfile = open(completefilename, "w")
			pickle.dump(self, outfile)
			outfile.close()
		except:
			raise
		else:
			if not quiet:
				print "Test summary saved on file '%s'. " % completefilename
			return completefilename

def testload(filename, quiet = False):
	infile = open(filename, "r")
	test = pickle.load(infile)
	infile.close()
	if isinstance(test, Test):
		if not quiet:
			print "Test summary loaded from file '%s'. " % filename
		return test
	else:
		raise InvalidCommandException, "Not a valid Test() instance"

if __name__ == "__main__":
	test = Test("Foo Bar")

	test.addSubtest('SetUp', task = True)
	test.addSubtestTitle('SetUp', "Initial configuration")
	test.begin('SetUp')
	test.end('SetUp', TEST_OK)

	test.addSubtest('FirstTest')
	test.addSubtestTitle('FirstTest', "Just a test")
	test.addSubtestDependency('FirstTest', 'SetUp')

	try:
		test.begin('FirstTest')
		test.addResult('FirstTest', 'HelloInterval', 10)
		test.addResult('FirstTest', 'DeadInterval', 40)
		test.addResult('FirstTest', 'Flags', 'E+M')
	except TestDependencyException:
		test.end('FirstTest', TEST_SKIPPED)
	except Exception, err:
		print type(err), err
		test.end('FirstTest', TEST_FAILED)
	except:
		raise
	else:
		test.end('FirstTest', TEST_OK)

	test.addSubtest(2)
	test.addSubtestTitle(2, "Another test")
	test.begin(2)
	test.end(2, TEST_FAILED)

	test.addSubtestTitle('3', "And another one")
	test.addSubtestDependency('3', 2)

	try:
		test.begin('3')
		test.addResult('3', 'Supercapsule', "OK!")
	except TestDependencyException:
		test.end('3', TEST_SKIPPED)
	except Exception, err:
		print type(err), err
		test.end('3', TEST_FAILED)
	except: 
		raise
	else:
		test.end('3', TEST_OK)

	print test
	print test.getTeX()

	savedfile = test.save()
	del test 
	test = testload(savedfile)
	print test
	test.save(dir = "/tmp")


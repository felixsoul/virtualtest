#!/usr/bin/python
from testsummary import *
from init_testbed3 import *

topofilename = "testbed2.yaml"
test = Test("First test")
test.addSubtest('InitialTestbed', task = True)
test.addSubtestTitle('InitialTestbed', "Initial testbed")

test.begin('InitialTestbed')
network = CreateNetWork(topofilename)
vfw=CreateVFW(topofilename)
#vm[0].setIPaddr(vm[0].interface[1].name, vm[0].interface[1].ipaddr, vm[0].interface[1].netmask)
#vm[1].setIPaddr(vm[1].interface[1].name, vm[1].interface[1].ipaddr, vm[1].interface[1].netmask)
test.end('InitialTestbed', TEST_OK)

#test.addSubtest('Ping')
#test.addSubtestTitle('Ping', 'Ping test')
#test.addSubtestDependency('Ping', 'InitialTestbed')
#test.begin('Ping')
#result = vm[0].ping(vm[0].interface[1].name, vm[1].interface[1].ipaddr, '10', '30')
#test.end('Ping', result)
#print test
#test.save()

#test.addSubtest('FTP')
#test.addSubtestTitle('FTP', 'FTP test')
#addSubtestDependency('FTP', 'InitialTestbed')
#test.begin('FTP')
#result = 





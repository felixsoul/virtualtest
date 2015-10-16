#!/usr/bin/python
import os
import sys
sys.path.insert(0, '../lib/')
from testsummary import *
from Vm import *
from Network import *

topofilename = "../topo/two_pc.yaml"
test = Test("First test")
test.addSubtest('InitialTestbed', task = True)
test.addSubtestTitle('InitialTestbed', "Initial testbed")

test.begin('InitialTestbed')
network = CreateNetWork(topofilename)
vm=CreateVM(topofilename)
vm[0].setIPaddr(vm[0].interface[1].name, vm[0].interface[1].ipaddr, vm[0].interface[1].netmask)
vm[1].setIPaddr(vm[1].interface[1].name, vm[1].interface[1].ipaddr, vm[1].interface[1].netmask)
test.end('InitialTestbed', TEST_OK)

test.addSubtest('Ping')
test.addSubtestTitle('Ping', 'Ping test')
test.addSubtestDependency('Ping', 'InitialTestbed')
test.begin('Ping')
result = vm[0].ping(vm[0].interface[1].name, vm[1].interface[1].ipaddr, '10', '30')
test.end('Ping', result)

test.addSubtest('Clean testbed')
DeleteVM(vm)
DeleteNetwork(network)
test.end('Clean testbed', TEST_OK)

print test
test.save()

#test.addSubtest('FTP')
#test.addSubtestTitle('FTP', 'FTP test')
#addSubtestDependency('FTP', 'InitialTestbed')
#test.begin('FTP')
#result = 





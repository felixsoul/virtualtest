#!/usr/bin/python
import yaml
import re
import subprocess 
import shlex
import sys
import time
import os
import shutil
import getpass 
import copy
import libvirt
import paramiko
import threading
#import unittest
import inspect
from obj import *
from Vm import *
from xml.dom.minidom import Document
from xml.etree import ElementTree as ET
from lxml import etree
from itertools import groupby
from pprint import pprint




Failure = 0
Success = 1
TEST_OK = 1
TEST_FAILED = 0
TEST_SKIPPED = 2
DefaultDir = '/var/log/waf'
SrcDir = '/home/xhshi/images'
CONN = libvirt.open('qemu:///system')
DNSMASQ_LEASEDIR = '/var/lib/libvirt/dnsmasq/'
topofilename = ''

timestr = time.strftime("%Y%m%d-%H%M%S")

if not os.path.exists(DefaultDir):
    os.makedirs(DefaultDir)

      
def toparams(*args):
    str1 = [item if isinstance(item, str) else " ".join(item) for item in args]
    params = ' '.join(str1)
    return params

def ExecCmd(cmd):
    p = subprocess.Popen([cmd], stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
    out, err = p.communicate()
    print p.returncode
    if p.returncode !=0:
        raise RuntimeError("%r failed, status code %s stdout %r stderr %r" %(cmd, p.returncode, out, err))
        return Failure
    else:
        return Success


#class obj(object):
#    def __init__(self, d):
#        for a, b in d.items():
#            if isinstance(b, (list, tuple)):
#                setattr(self, a, [obj(x) if isinstance(x, dict) else x for x in b])
#            else:
#                setattr(self, a, obj(b) if isinstance(b, dict) else b)



#class Vm(obj):
#    def __init__(self,d):
#        obj.__init__(self,d)
#        self.VmDir = DefaultDir+'/'+timestr+'/'+self.name
#        self.name = getpass.getuser()+'-'+self.name
#        self.ssh = paramiko.SSHClient()
#        self.ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
#
#        if not os.path.exists(self.VmDir):
#            os.makedirs(self.VmDir)
#        
#        src_files = os.listdir(self.image)
#        for file_name in src_files:
#            full_file_name = os.path.join(self.image,file_name)
#            if (os.path.isfile(full_file_name)):
#                shutil.copy(full_file_name, self.VmDir)
#         
#         
#    def OsType(self):
#        ostype = '--os-type '+self.ostype+' '
#        return ostype
#    
#    def VirtType(self):
#        virttype = '--virt-type '+self.virttype+' '
#        return virttype
#     
#    def Ram(self):
#        self.ram = str(self.ram)
#        ram= '--ram '+self.ram+' '
#        return ram
#
#    def Vcpus(self):
#        self.vcpus=str(self.vcpus)
#        vcpus = '--vcpus '+self.vcpus+' '
#        return vcpus
#    
#    def Boot(self):
#        boot = '--boot '+self.boot+' '
#        return boot
#    
#    def Disk(self):
#        disk=[]
#        for item in self.disk:
#            item.diskpath = self.VmDir+'/'+item.diskpath
#            print item.diskpath
#            disk.append("--disk path=%s,device=%s,bus=%s,format=%s "% (item.diskpath, item.device, item.bus, item.format))
#        return disk
#
#    def NetItem(self):
#        netops=[]
#        for item in self.network:
#            netops.append ("--network network=%s,model=%s" % (item.subnet,item.model))
#        #print netops
#        return netops
#
#    def VmName(self):
#        vmname = '--name '+self.name+' '
#        print self.name
#        return vmname
#
#    def serialport(self):
#        if hasattr(self, 'port'):  
#            serialport = '--serial tcp,host=0.0.0.0:'+str(self.port)+',mode=bind,protocol=telnet '
#        else:
#            serialport =''
#        print serialport
#        return serialport
#    
#    def CreateVm(self):
#        cmd = toparams ("virt-install --noautoconsole ", self.VmName(), self.OsType(), self.VirtType(), self.Ram(), self.Vcpus(), self.Boot(), self.Disk(), self.serialport(), self.NetItem())
#        print cmd
#        result=ExecCmd(cmd)
#        print result
#        if result == Failure:
#            print "Create %s failed." % self.VmName()
#        else:
#            print "Create %s sucessfully." % self.VmName()
#
#    def DeleteVm(self):
#        cmd = [ toparams ("virsh destroy ", self.name), toparams ("virsh undefine ", self.name)]
#        for itemcmd in cmd:
#            result = ExecCmd(itemcmd)
#            if result == Failure:
#                print "Destroy or undefine %s failed." % self.name
#            else:
#                print "Destroy or undefine %s sucessfully." % self.name
#    
#    def RmVmFile(self):
#        disk=[]
#        for item in self.disk:
#            cmd = toparams ("rm -fr ", item.diskpath)
#            result = ExecCmd(cmd)
#            if result == Failure:
#                print "Delete VM %s disk %s failed." % (self.name, item.diskpath)
#            else:
#                print "Delete VM %s disk %s sucessfully." % (self.name, item.diskpath)
#
#    def GetDomain(self):
#        self.dom = CONN.lookupByName(self.name)
#        if self.dom == None:
#            print('Failed to find the domain' + self.name)
#            exit(1)
#    
#    def RetrieveInterface(self):
#        self.GetDomain()
#        self.interface =[]
#        xe = ET.fromstring(self.dom.XMLDesc(0))
#        i = 0
#        for iface in xe.findall('.//devices/interface'):
#            print i
#            self.interface.append(Interface())
#            self.interface[i].mac = iface.find('mac').get('address')
#            self.interface[i].vname = iface.find('target').get('dev')
#            self.interface[i].vnet = iface.find('source').get('network')
#            if hasattr(self.network[i], 'ipaddr'):
#                self.interface[i].ipaddr=self.network[i].ipaddr
#                self.interface[i].netmask=self.network[i].netmask
#            else:
#                pass
#            i=+1
#    
#    def GetAdminIP(self):
#        self.GetDomain()
#        self.adminmac = self.interface[0].mac
#        self.adminIP=''
#        DNSMASQ_LEASE=DNSMASQ_LEASEDIR+self.interface[0].vnet+'.leases'
#        start_time  = time.time()
#        while(self.adminIP == '') :
#            with open(DNSMASQ_LEASE) as lease_file:
#                for line in lease_file:
#                    line_split = line.split()
#                    if self.adminmac == line_split[1]:
#                        self.adminIP = line_split[2]
#                        self.interface[0].ipaddr =self.adminIP
#                        print self.adminIP
#                end_time = time.time()
#                time_taken = end_time - start_time
#            if (time_taken > 180):
#                print "Something is wrong. The VM %s can't obtain IP address." %self.name
#                exit(1)
#     
#    def cmd(self,*args):
#        self.ssh.connect(self.adminIP, username=self.username, password=self.password)
#        self.session = self.ssh.get_transport().open_session()
#        command = toparams(*args)
#        self.session.exec_command(command)
#        returncode = self.session.recv_exit_status()
#        if returncode !=0:
#            raise RuntimeError("%r failed, status code %s stdout %r " %(command, returncode,self.session.recv(1024)))
#            self.ssh.close()
#        else:
#            self.ssh.close()
#            output = self.session.recv(1024)
#            print "cmd output %s" %output
#            return output
#
#    def getInterfaceName(self):
#        output = self.cmd('ls /sys/class/net')
#        interfaces=output.split()
#        for interfacename in interfaces:
#            command = 'cat /sys/class/net/'+interfacename+'/address'
#            macaddr = self.cmd(command)
#            i=0
#            for interface in self.interface:
#                if str(interface.mac).strip() == str(macaddr).strip():
#                    self.interface[i].name=interfacename
#                    continue
#                else:
#                    i=i+1
#    def setIPaddr(self,interfacename,ipaddr,netmask):
#        arg = ipaddr+'/'+str(netmask)
#        print arg
#        self.cmd('ifconfig',interfacename,arg)
#    
#    def ping(self, srcif, dstIP, count, tolerance):
#        output = self.cmd('ping',dstIP,'-I', srcif, '-c',count)
#        print output
#        match = re.search('(\d*)% packet loss', output)
#        pkt_loss = match.group(1)
#        if pkt_loss < tolerance:
#            return TEST_OK
#        else:
#            print "The loss rate %d% is larger than tolerance %d%." % (pkt_loss, tolerance)
#            return TEST_FAILED

    #def ftp(self, dstIP, size):

#class Interface:
#    def __init__(self):
#        self.vname = ''
#        self.mac =''
#        self.name =''
#        self.ipaddr = ''
#        self.netmask = ''
   
#class Network:
#   def __init__(self):
#       self.dict={}
#       self.Dir = DefaultDir+'/'+timestr
#       self.netName = ''
#       if not os.path.exists(self.Dir):
#           os.makedirs(self.Dir)

#   def setDict(self,d):
#       self.dict = {'network':d}
#       
#   def setNames(self):
#       self.netName = self.dict['network']['name'][0]['__text__']
#       self.fileName = os.path.join(self.Dir,self.netName)

#   def d2xml(self):
#       d=self.dict
#       def _d2xml(d, p):
#           for k,v in d.items():
#               if isinstance(v,dict):
#                   node = etree.SubElement(p, k)
#                   _d2xml(v, node)
#               elif isinstance(v,list):
#                   for item in v:
#                       node = etree.SubElement(p, k)
#                       _d2xml(item, node)
#               elif k == "__text__":
#                       p.text = v
#               elif k == "__tail__":
#                       p.tail = v
#               else:
#                   p.set(k, v)

#       k,v = d.items()[0]
#       node = etree.Element(k)
#       _d2xml(v, node)
#       return node

#   def generateXml(self):
#       self.setNames()
#       netFile = open(self.fileName,"w")
#       netFile.write(etree.tostring(self.d2xml()))
#       netFile.close()

#   def CreateNet(self):
#       self.generateXml()
#       cmd = [toparams ("virsh net-define ", self.fileName), toparams("virsh net-start ", self.netName), toparams("virsh net-autostart ", self.netName)]
#       for itemcmd in cmd:
#           result = ExecCmd(itemcmd)
#           if result == Failure:
#               print "Create %s failed." % self.netName
#           else:
#               print "Create %s sucessfully." % self.netName

#   def DeleteNet(self):
#       cmd = [toparams("virsh net-destroy ", self.netName), toparams("virsh net-undefine ", self.netName)]
#       for itemcmd in cmd:
#           result = ExecCmd(itemcmd)
#           if result == Failure:
#               print "Destroy or undefine network %s failed." % self.netName
#           else:
#               print "Destroy or undefine network %s sucessfully." % self.netName
#   
#   def RmNetFile(self):
#       cmd = toparams ("rm -fr ", self.fileName)
#       result = ExecCmd(cmd)
#       if result == Failure:
#           print "Delete VM %s disk %s failed." % (self.name, item.diskpath)
#       else:
#           print "Delete VM %s disk %s sucessfully." % (self.name, item.diskpath)
      

def CreateNetWork(topofilename):
    f = open(topofilename)
    x = yaml.load(f)
    netgroup = x['net']
    networks = []
    network=[]
    for item in netgroup:
        networks.append(item)
        network.append(Network())
    i=0
    for item in networks:
        network[i].setDict(item)
        network[i].CreateNet()
        i=i+1
    return network

def CreateVM(topofilename):
    f = open(topofilename)
    x = yaml.load(f)
    vmgroup = x['vm']
    vm=[]
    for item in vmgroup:
        vm.append(Vm(item))
    i=0 
    for item in vm:
        vm[i].CreateVm()
        vm[i].RetrieveInterface()
        vm[i].GetAdminIP()
        vm[i].getInterfaceName()
        i=i+1
    return vm


def store_result(f):
    print f
    def wrapped(self):
        if 'result' not in self.__dict__:
            self.results=[]
        try:
            result = f(self)
        except Exception as e:
            self.results[f.__name__] = {'success':False, 'locals': inspect.trace()[-1][0].f_locals}
            raise e
        self.results[f.__name__] = {'success': True, 'result': result}
        return result
    return wrapped
"""
class Test(unittest.TestCase):
    #topofilename = ''
    @classmethod
    def setUpClass(cls):
        pass
setup_done = False
class BasicTest(Test):
    topofilename ='ABC'
    
    @classmethod
    def setUpClass(self):
        super(Test,self).setUpClass()
        print 'Init'
        print self.topofilename
        self.network = CreateNetWork(self.topofilename)
        self.vm=CreateVM(self.topofilename)
        self.vm[0].setIPaddr(self.vm[0].interface[1].name, self.vm[0].interface[1].ipaddr, self.vm[0].interface[1].netmask)
        self.vm[1].setIPaddr(self.vm[1].interface[1].name, self.vm[1].interface[1].ipaddr, self.vm[1].interface[1].netmask)
    #    super(Test,cls).setUpClass()
    #    print cls.topofilename
    #    f = open(cls.topofilename)
    #    x = yaml.load(f)
    #    vmgroup = x['vm']
    #    netgroup = x['net']
    #    networks = []
    #    vm=[]
    #    netwoks=[]
    #    network=[]
    #    for item in netgroup:
    #        networks.append(item)
    #        network.append(Network())
    #    i=0
    #    for item in networks:
    #        network[i].setDict(item)
    #        network[i].CreateNet()
    #        i=i+1
    #    for item in vmgroup:
    #        vm.append(Vm(item))
    #    i=0 
    #    for item in vm:
    #        vm[i].CreateVm()
    #        vm[i].RetrieveInterface()
    #        vm[i].GetAdminIP()
    #        vm[i].getInterfaceName()
    #        i=i+1
#
    #    vm[0].setIPaddr(vm[0].interface[1].name, vm[0].interface[1].ipaddr, vm[0].interface[1].netmask)
    #    vm[1].setIPaddr(vm[1].interface[1].name, vm[1].interface[1].ipaddr, vm[1].interface[1].netmask)

    #def setUp(self):
    #    print 'Init'
    #    print self.topofilename
    #    if setup_done:
    #        return
    #    setup_done = True
    #    self.network = CreateNetWork(self.topofilename)
    #    self.vm=CreateVM(self.topofilename)
        
        #f = open(self.topofilename)
        #x = yaml.load(f)
        #vmgroup = x['vm']
        #netgroup = x['net']
        #networks = []
        #self.vm=[]
        #netwoks=[]
        #self.network=[]
        #for item in netgroup:
        #    networks.append(item)
        #    self.network.append(Network())
        #i=0
        #for item in networks:
        #    self.network[i].setDict(item)
        #    self.network[i].CreateNet()
        #    i=i+1
        #for item in vmgroup:
        #    self.vm.append(Vm(item))
        #i=0 
        #for item in self.vm:
        #    self.vm[i].CreateVm()
        #    self.vm[i].RetrieveInterface()
        #    self.vm[i].GetAdminIP()
        #    self.vm[i].getInterfaceName()
        #    i=i+1
    #    self.vm[0].setIPaddr(self.vm[0].interface[1].name, self.vm[0].interface[1].ipaddr, self.vm[0].interface[1].netmask)
    #    self.vm[1].setIPaddr(self.vm[1].interface[1].name, self.vm[1].interface[1].ipaddr, self.vm[1].interface[1].netmask)
        
    #@store_result
    def test_Ping(self):
        print "Ping test"
        result=self.vm[0].ping(self.vm[0].interface[1].name, self.vm[1].interface[1].ipaddr, '10', '30')
        self.assertTrue(result, Success)
    
    #@store_result
    def test_Ping2(self):
        print "Ping test"
        result=self.vm[0].ping(self.vm[0].interface[1].name, self.vm[1].interface[1].ipaddr, '5', '30')
        self.assertTrue(result, Success)
#def main(argv):
#    topofilename = sys.argv[1]
#    print topofilename
    #unittest.main()

def suite_results(suite):
    ans = {}
    print suite
    for test in suite:
        print test.__dict__
        if 'results' in test.__dict__:
            ans.update(test.results)
    return ans



if __name__ == '__main__':
    BasicTest.topofilename = sys.argv.pop()
    suite = unittest.TestLoader().loadTestsFromTestCase(BasicTest)
    #result = unittest.TestResult()
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    print type(result)
    print "There are %d testcases run." %result.testsRun
    print result.__dict__
    #unittest.TextTestRunner(verbosity=2).run(suite)

    #pprint(suite_results(suite))
#f=open('testbed1.yaml')
#x=yaml.load(f)
#vmgroup=x['vm']
#netgroup = x['net']
#vm=[]
#networks=[]
#network=[]
#
#for item in netgroup:
#    networks.append(item)
#    network.append(Network())
#i=0
#for item in networks:
#    network[i].setDict(item)
#    network[i].CreateNet()
#    i=i+1
##print e[0]
##network = Network()
#
#
#
#for item in vmgroup:
#    vm.append(Vm(item))
#i=0 
#for item in vm:
#    vm[i].CreateVm()
#    vm[i].RetrieveInterface()
#    vm[i].GetAdminIP()
#    vm[i].getInterfaceName()
#    i=i+1
#vm[0].CreateVm()
#vm[0].RetrieveInterface()
#print vm[0].interface[0].vname
#print vm[0].interface[0].vnet
#print vm[0].interface[0].mac
#
#print vm[0].interface[1].vname
#print vm[0].interface[1].vnet
#print vm[0].interface[1].mac
#vm[0].GetAdminIP()
#print vm[0].adminIP
#vm[0].getInterfaceName()
#print vm[0].adminIP
#print vm[0].interface[1].ipaddr
#print vm[0].interface[1].name
#print vm[0].interface[1].netmask
#print vm[1].interface[1].ipaddr
#print vm[1].interface[1].name
#print vm[1].interface[1].netmask
#print vm[0].setIPaddr(vm[0].interface[1].name, vm[0].interface[1].ipaddr, vm[0].interface[1].netmask)
#print vm[1].setIPaddr(vm[1].interface[1].name, vm[1].interface[1].ipaddr, vm[1].interface[1].netmask)
#
#print vm[0].ping(vm[0].interface[1].name, vm[1].interface[1].ipaddr, '10', '30')


#e[0].CreateVm()
#e[0].DeleteVm()
#e[0].RmVmFile()
#for item in e:
    #item.CreateVm()
#for item in e:
#    item.DeleteVm()

#print netgroup


#print etree.tostring(network.d2xml())


    
#network = {'network':e[0]}
#xml=dict2xml(network)
#xml.display()
#print e[0].__dict__
#print netgroup[0]
#d = {'network': {'ip': [{'netmask': '255.255.255.0', 'address': '192.168.212.1'}, {'dhcp': {'range': 'start: 192.169.212.2,end: 192.168.212.5'}}],  'name': 'mgt-net'}}
#print serialize(d)

#timestr = time.strftime("%Y%m%d-%H%M%S")
#print timestr
"""

#!/usr/bin/python
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
import yaml

from xml.dom.minidom import Document
from xml.etree import ElementTree as ET

from  GlobalConfig import *
from obj import *
from Interface import *

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

class Vm(obj):
    def __init__(self,d):
        obj.__init__(self,d)
        self.VmDir = DefaultDir+'/'+timestr+'/'+self.name
        self.name = getpass.getuser()+'-'+self.name
        self.ssh = paramiko.SSHClient()
        self.ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        if not os.path.exists(self.VmDir):
            os.makedirs(self.VmDir)
        
        src_files = os.listdir(self.image)
        for file_name in src_files:
            full_file_name = os.path.join(self.image,file_name)
            if (os.path.isfile(full_file_name)):
                shutil.copy(full_file_name, self.VmDir)
         
         
    def OsType(self):
        ostype = '--os-type '+self.ostype+' '
        return ostype
    
    def VirtType(self):
        virttype = '--virt-type '+self.virttype+' '
        return virttype
     
    def Ram(self):
        self.ram = str(self.ram)
        ram= '--ram '+self.ram+' '
        return ram
    def Vcpus(self):
        self.vcpus=str(self.vcpus)
        vcpus = '--vcpus '+self.vcpus+' '
        return vcpus
    
    def Boot(self):
        boot = '--boot '+self.boot+' '
        return boot
    
    def Disk(self):
        disk=[]
        for item in self.disk:
            item.diskpath = self.VmDir+'/'+item.diskpath
            print item.diskpath
            disk.append("--disk path=%s,device=%s,bus=%s,format=%s "% (item.diskpath, item.device, item.bus, item.format))
        return disk
    def NetItem(self):
        netops=[]
        for item in self.network:
            netops.append ("--network network=%s,model=%s" % (item.subnet,item.model))
        #print netops
        return netops
    def VmName(self):
        vmname = '--name '+self.name+' '
        print self.name
        return vmname
    def serialport(self):
        if hasattr(self, 'port'):  
            serialport = '--serial tcp,host=0.0.0.0:'+str(self.port)+',mode=bind,protocol=telnet '
        else:
            serialport =''
        print serialport
        return serialport
    
    def CreateVm(self):
        cmd = toparams ("virt-install --noautoconsole ", self.VmName(), self.OsType(), self.VirtType(), self.Ram(), self.Vcpus(), self.Boot(), self.Disk(), self.serialport(), self.NetItem())
        print cmd
        result=ExecCmd(cmd)
        print result
        if result == Failure:
            print "Create %s failed." % self.VmName()
        else:
            print "Create %s sucessfully." % self.VmName()
    def DeleteVm(self):
        cmd = [ toparams ("virsh destroy ", self.name), toparams ("virsh undefine ", self.name)]
        for itemcmd in cmd:
            result = ExecCmd(itemcmd)
            if result == Failure:
                print "Destroy or undefine %s failed." % self.name
            else:
                print "Destroy or undefine %s sucessfully." % self.name
    
    def RmVmFile(self):
        disk=[]
        for item in self.disk:
            cmd = toparams ("rm -fr ", item.diskpath)
            result = ExecCmd(cmd)
            if result == Failure:
                print "Delete VM %s disk %s failed." % (self.name, item.diskpath)
            else:
                print "Delete VM %s disk %s sucessfully." % (self.name, item.diskpath)
    def GetDomain(self):
        self.dom = CONN.lookupByName(self.name)
        if self.dom == None:
            print('Failed to find the domain' + self.name)
            exit(1)
    
    def RetrieveInterface(self):
        self.GetDomain()
        self.interface =[]
        xe = ET.fromstring(self.dom.XMLDesc(0))
        i = 0
        for iface in xe.findall('.//devices/interface'):
            print i
            self.interface.append(Interface())
            self.interface[i].mac = iface.find('mac').get('address')
            self.interface[i].vname = iface.find('target').get('dev')
            self.interface[i].vnet = iface.find('source').get('network')
            if hasattr(self.network[i], 'ipaddr'):
                self.interface[i].ipaddr=self.network[i].ipaddr
                self.interface[i].netmask=self.network[i].netmask
            else:
                pass
            i=+1
    
    def GetAdminIP(self):
        self.GetDomain()
        self.adminmac = self.interface[0].mac
        self.adminIP=''
        DNSMASQ_LEASE=DNSMASQ_LEASEDIR+self.interface[0].vnet+'.leases'
        start_time  = time.time()
        while(self.adminIP == '') :
            with open(DNSMASQ_LEASE) as lease_file:
                for line in lease_file:
                    line_split = line.split()
                    if self.adminmac == line_split[1]:
                        self.adminIP = line_split[2]
                        self.interface[0].ipaddr =self.adminIP
                        print self.adminIP
                end_time = time.time()
                time_taken = end_time - start_time
            if (time_taken > 180):
                print "Something is wrong. The VM %s can't obtain IP address." %self.name
                exit(1)
     
    def cmd(self,*args):
        self.ssh.connect(self.adminIP, username=self.username, password=self.password)
        self.session = self.ssh.get_transport().open_session()
        command = toparams(*args)
        self.session.exec_command(command)
        returncode = self.session.recv_exit_status()
        if returncode !=0:
            raise RuntimeError("%r failed, status code %s stdout %r " %(command, returncode,self.session.recv(1024)))
            self.ssh.close()
        else:
            self.ssh.close()
            output = self.session.recv(1024)
            print "cmd output %s" %output
            return output
    def getInterfaceName(self):
        output = self.cmd('ls /sys/class/net')
        interfaces=output.split()
        for interfacename in interfaces:
            command = 'cat /sys/class/net/'+interfacename+'/address'
            macaddr = self.cmd(command)
            i=0
            for interface in self.interface:
                if str(interface.mac).strip() == str(macaddr).strip():
                    self.interface[i].name=interfacename
                    continue
                else:
                    i=i+1
    def setIPaddr(self,interfacename,ipaddr,netmask):
        arg = ipaddr+'/'+str(netmask)
        print arg
        self.cmd('ifconfig',interfacename,arg)
    
    def ping(self, srcif, dstIP, count, tolerance):
        output = self.cmd('ping',dstIP,'-I', srcif, '-c',count)
        print output
        match = re.search('(\d*)% packet loss', output)
        pkt_loss = match.group(1)
        if pkt_loss < tolerance:
            return TEST_OK
        else:
            print "The loss rate %d% is larger than tolerance %d%." % (pkt_loss, tolerance)
            return TEST_FAILED

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

def DeleteVM(vmlist):
    for item in vmlist:
        item.DeleteVm()
        item.RmVmFile()
    print "The VMs have been deleted."

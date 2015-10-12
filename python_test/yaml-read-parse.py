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
from xml.dom.minidom import Document

Failure = 0
Success = 1
DefaultDir = '/var/log/waf'
SrcDir = '/home/xhshi/images'

timestr = time.strftime("%Y%m%d-%H%M%S")

if not os.path.exists(DefaultDir):
    os.makedirs(DefaultDir)

class obj(object):
    def __init__(self, d):
        for a, b in d.items():
            if isinstance(b, (list, tuple)):
                setattr(self, a, [obj(x) if isinstance(x, dict) else x for x in b])
            else:
                setattr(self, a, obj(b) if isinstance(b, dict) else b)
        
def toparams(*args):
    str1 = [item if isinstance(item, str) else " ".join(item) for item in args]
    params = ''.join(str1)
    return params

def ExecCmd(cmd):
    p = subprocess.Popen([cmd], stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
    out, err = p.communicate()
    if len(out) == 0:
        print "Failure: " + err
        return Failure
    else:
        return Success


class Net(obj):
    def CreateNet(self):
        pass




class Vm(obj):
    def __init__(self,d):
        obj.__init__(self,d)
        self.VmDir = DefaultDir+'/'+timestr+'/'+self.name
        self.name = getpass.getuser()+'-'+self.name
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
    
    def CreateVm(self):
        cmd = toparams ("virt-install --noautoconsole ", self.VmName(), self.OsType(), self.VirtType(), self.Ram(), self.Vcpus(), self.Boot(), self.Disk(), self.NetItem())
        result=ExecCmd(cmd)
        print result
        if result == Failure:
            print "Create %s failed." % self.VmName()
        else:
            print "Create %s sucessfully." % self.VmName()


class dict2xml(object):
    doc = Document()
    def __init__(self,structure):
        if len(structure) == 1:
            rootName = str(structure.keys()[0])
            self.root = self.doc.createElement(rootName)
            self.doc.appendChild(self.root)
            self.build(self.root, structure[rootName])

    def build(self, father, structure):
        if type(structure) == dict:
            for k in structure:
                tag = self.doc.createElement(k)
                father.appendChild(tag)
                self.build(tag,structure[k])
        elif type(structure) == list:
            grandFather = father.parentNode
            tagName = father.tagName
            grandFather.removeChild(father)
            for l in structure:
                tag = self.doc.createElement(tagName)
                self.build(tag,l)
                grandFather.appendChild(tag)
        else:
            data = str(structure)
            tag = self.doc.createTextNode(data)
            father.appendChild(tag)

    def generate(self):
        return self.doc.toprettyxml(indent= " ")

f=open('topo-test.yaml')
x=yaml.load(f)
#vmgroup=x['vm']
netgroup = x['net']
e=[]
#print netgroup
#for item in vmgroup:
#    e.append(Vm(item))
#e[0].CreatVm()
#for item in e:
#    item.CreateVm()

for item in netgroup:
    print item
    network = {'network':item}
    xml = dict2xml(network)
    testDir = DefaultDir+'/'+timestr+'/' 
    if not os.path.exists(testDir):
        os.makedirs(testDir)
    full_file_name = os.path.join(testDir,item['name'])
    try:
        topo_file = open(full_file_name,'a')
    except:
        print "The topo file %s exists." %full_file_name
        sys.exit(0)
    topo_file.write(xml.generate())
    topo_file.close()
    
#network = {'network':e[0]}
#xml=dict2xml(network)
#xml.display()
#print e[0].__dict__
#print netgroup[0]
#d = {'network': {'ip': [{'netmask': '255.255.255.0', 'address': '192.168.212.1'}, {'dhcp': {'range': 'start: 192.169.212.2,end: 192.168.212.5'}}],  'name': 'mgt-net'}}
#print serialize(d)

#timestr = time.strftime("%Y%m%d-%H%M%S")
#print timestr

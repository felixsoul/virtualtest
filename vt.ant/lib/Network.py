#!/usr/bin/python
import os
import yaml

from xml.dom.minidom import Document
from xml.etree import ElementTree as ET
from lxml import etree
from itertools import groupby

from GlobalConfig import *
from Common import * 

class Network:
    def __init__(self):
        self.dict={}
        self.Dir = DefaultDir+'/'+timestr
        self.netName = ''
        if not os.path.exists(self.Dir):
            os.makedirs(self.Dir)
    def setDict(self,d):
        self.dict = {'network':d}
        
    def setNames(self):
        self.netName = self.dict['network']['name'][0]['__text__']
        self.fileName = os.path.join(self.Dir,self.netName)
    def d2xml(self):
        d=self.dict
        def _d2xml(d, p):
            for k,v in d.items():
                if isinstance(v,dict):
                    node = etree.SubElement(p, k)
                    _d2xml(v, node)
                elif isinstance(v,list):
                    for item in v:
                        node = etree.SubElement(p, k)
                        _d2xml(item, node)
                elif k == "__text__":
                        p.text = v
                elif k == "__tail__":
                        p.tail = v
                else:
                    p.set(k, v)
        k,v = d.items()[0]
        node = etree.Element(k)
        _d2xml(v, node)
        return node
    def generateXml(self):
        self.setNames()
        netFile = open(self.fileName,"w")
        netFile.write(etree.tostring(self.d2xml()))
        netFile.close()
    def CreateNet(self):
        self.generateXml()
        cmd = [toparams ("virsh net-define ", self.fileName), toparams("virsh net-start ", self.netName), toparams("virsh net-autostart ", self.netName)]
        for itemcmd in cmd:
            result = ExecCmd(itemcmd)
            if result == Failure:
                print "Create %s failed." % self.netName
            else:
                print "Create %s sucessfully." % self.netName
    def DeleteNet(self):
        cmd = [toparams("virsh net-destroy ", self.netName), toparams("virsh net-undefine ", self.netName)]
        for itemcmd in cmd:
            result = ExecCmd(itemcmd)
            if result == Failure:
                print "Destroy or undefine network %s failed." % self.netName
            else:
                print "Destroy or undefine network %s sucessfully." % self.netName
    
    def RmNetFile(self):
        cmd = toparams ("rm -fr ", self.fileName)
        result = ExecCmd(cmd)
        if result == Failure:
            print "Delete net %s netFile %s failed." % (self.name, self.fileName)
        else:
            print "Delete net %s netFile %s sucessfully." % (self.netName, self.fileName)

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

def DeleteNetwork(Networklist):
    for item in Networklist:
        item.DeleteNet()
        item.RmNetFile()
    print "The networks have been removed."
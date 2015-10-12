#!/usr/bin/python
import yaml
import libvirt
import os
import sys

class ParseYaml(object):
    def __init__(self,*initial_data, **kwargs):
        for dictionary in initial_data:
            for key in dictionary:
                setattr(self,key,dictionary[key])
        for key in kwargs:
            setattr(self,key,kwargs[key])
      

class Vm(ParseYaml):
    def Create(self):
        return self.network
        #print self.Network.subnet


f=open('testbed.yaml')
x=yaml.load(f)
vmgroup=x['vm']
print vmgroup
i=0
e=[]
network=[]
for item in vmgroup:
    e.append(Vm(item))
#print e[0].network[0].subnet
#for item in e[0].network:
#    network.append(ParseYaml(item))
#print network[0].subnet
#print network[1].subnet
###print ("virt-install \
#             --name %s \
#             --os-type linux \
#             --virt-type kvm \
#             --accelerate \
#             --ram 2048 \
#             -- vcpus 2 \
#             --boot hd \
#             --disk path= %s \
#             --network" %(e[0].name,e[0].disk))
###


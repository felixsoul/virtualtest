#!/usr/bin/python

#from __future__ import print_function
import sys
import libvirt
from xml.dom import minidom
from xml.etree import ElementTree as ET

def print_entry(key, value):
    print "%-10s %-10s" % (key, value)

def print_xml(key, ctx, path):
    res = ctx.xpathEval(path)
    if res is None or len(res) == 0:
        value="Unknown"
    else:
        value = res[0].content
    print_entry(key, value)
    return value
conn = libvirt.open('qemu:///system')
domName = 'xhshi-testpc1'
dom = conn.lookupByName(domName)
if dom == None:
    print('Failed to find the domain '+domName)
    exit(1)

xe = ET.fromstring(dom.XMLDesc(0))
for iface in xe.findall('.//devices/interface'):
    mac = iface.find('mac').get('address')
    iface_name = iface.find('target').get('dev')
    iface_net = iface.find('source').get('network')
    print iface_name
    print iface_net

conn.close()
exit(0)



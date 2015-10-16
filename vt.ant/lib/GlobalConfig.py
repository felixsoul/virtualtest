#!/usr/bin/python
import libvirt
import os
import time

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
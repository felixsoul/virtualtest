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

f=open('topo-test1.yaml')
x=yaml.load(f)
#vmgroup=x['vm']
netgroup = x['network']
e=[]
print netgroup

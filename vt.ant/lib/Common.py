#!/usr/bin/python
import subprocess 
from GlobalConfig import *

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
#!/usr/bin/env python
from lxml import etree
from itertools import groupby
import yaml
import sys

def xml2d(e):
    """Convert an etree into a dict structure

    @type  e: etree.Element
    @param e: the root of the tree
    @return: The dictionary representation of the XML tree
    """
    def _xml2d(e):
        kids = dict(e.attrib)
        if e.text:
            kids['__text__'] = e.text
        if e.tail:
            kids['__tail__'] = e.tail
        for k, g in groupby(e, lambda x: x.tag):
            g = [ _xml2d(x) for x in g ] 
            kids[k]=  g
        return kids
    return { e.tag : _xml2d(e) }


def d2xml(d):
    """convert dict to xml

       1. The top level d must contain a single entry i.e. the root element
       2.  Keys of the dictionary become sublements or attributes
       3.  If a value is a simple string, then the key is an attribute
       4.  if a value is dict then, then key is a subelement
       5.  if a value is list, then key is a set of sublements

       a  = { 'module' : {'tag' : [ { 'name': 'a', 'value': 'b'},
                                    { 'name': 'c', 'value': 'd'},
                                 ],
                          'gobject' : { 'name': 'g', 'type':'xx' },
                          'uri' : 'test',
                       }
           }
    >>> d2xml(a)
    <module uri="test">
       <gobject type="xx" name="g"/>
       <tag name="a" value="b"/>
       <tag name="c" value="d"/>
    </module>

    @type  d: dict 
    @param d: A dictionary formatted as an XML document
    @return:  A etree Root element
    """
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
    
    

if __name__=="__main__":

    #X = """<T uri="boo"><a n="1"/><a n="2"/><b n="3"><c x="y"/></b></T>"""
    #print X
    X =  "<network> <name>mgt-net</name> <bridge name='mgt-net' stp='n' delay='0' /> <forward mode='nat'/> <ip address='192.168.211.1' netmask='255.255.255.0'> <dhcp> <range start='192.168.211.2' end='192.168.211.5'/> </dhcp> </ip> </network>"
    #Y = xml2d(etree.XML(X))
    #Y = {'network': {'forward': [{'mode': 'nat'}],'ip': [{'netmask': '255.255.255.0', 'dhcp': [{'range': [{'start': '192.168.211.2', 'end': '192.168.211.5'}]}], 'address': '192.168.211.1'}], 'name': [{'__text__': 'mgt-net'}], 'bridge': [{'delay': '0', 'stp': 'n', 'name': 'mgt-net'}]}}
    #print Y

    f=open('topo-test.yaml')
    x=yaml.load(f)
    #vmgroup=x['vm']
    Y = x['net']
    #print Y
    Y = {'forward': [{'mode': 'nat'}], 'bridge': [{'delay': '0', 'stp': 'n', 'name': 'mgt-net'}], 'name': [{'__text__': 'mgt-net'}], 'ip': [{'dhcp': [{'range': [{'start': '192.168.211.2', 'end': '192.168.211.5'}]}], 'netmask': '255.255.255.0', 'address': '192.168.211.1'}]}
    item = {'network':Y}
    Z = etree.tostring (d2xml(item) )
    print Z
    #with open('result.yml', 'w') as yaml_file:
    #        yaml_file.write( yaml.dump(Y, default_flow_style=False))
    #assert X == Z

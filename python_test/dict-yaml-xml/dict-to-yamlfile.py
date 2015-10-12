#!/usr/bin/python

import yaml

data = dict(
    A = 'a',
    B = dict(
        C = 'c',
        D = 'd',
        E = 'e',
    )
)

with open('data.yml', 'w') as outfile:
    outfile.write( yaml.dump(data, default_flow_style=True) )
with open('data1.yml', 'w') as outfile:
    outfile.write( yaml.dump(data, default_flow_style=False) )


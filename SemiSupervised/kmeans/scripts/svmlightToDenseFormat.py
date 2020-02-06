#!/usr/bin/python
import fileinput
for line in fileinput.input():
    vals=[]
    for token in line.split()[1:]:
        posn, val = token.split(":")
        vals.append(val)
    print ','.join(vals)


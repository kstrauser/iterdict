#!/usr/bin/env python

from iterdict import IterDict

n = 1000000

d = IterDict()
# d = dict()

print 'Inserting'
for i in range(n):
    d[i] = i

print 'Deleting'
for i in range(n):
    del d[i]

print d

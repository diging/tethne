# !/usr/bin/python

import os, sys

# using command mkdir
a = 'cat text.txt'

b = os.popen(a,'r',1)

print b, type(b)

for line in b.readlines():
	print line
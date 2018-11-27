#!/bin/python

import numpy as np

print('a = np.array([-1, 0, 1, 2, 3], dtype=float)')
a = np.array([-1, 0, 1, 2, 3], dtype=float)
print(a)
print('dividido por')
print('b = np.array([ 0, 0, 0, 2, 2], dtype=float)')
b = np.array([ 0, 0, 0, 2, 2], dtype=float)
print(b)
print('comando: c = np.divide(a, b, out=np.zeros_like(a), where=b!=0)')
# If you don't pass `out` the indices where (b == 0) will be uninitialized!
c = np.divide(a, b, out=np.zeros_like(a), where=b!=0)
print('igual a')
print(c)
print('Comando c=a/b gera erro:')
c=a/b
print('Comando c.clip(min=0)')
print(c.clip(min=0))
print('c agora e:')
print(c)
print('comando c *= (c>0)')
c *= (c>0)
print('c agora e:')
print(c)


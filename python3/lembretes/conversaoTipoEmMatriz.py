#!/bin/python

import numpy as np

print('a = np.array([-1, 0, 1, 3, 2], dtype=float)')
a = np.array([-1, 0, 1, 3, 2], dtype=float)
print(a)
print('a.astype(int)')
print(a.astype(int))
print('b = np.array([-1, 1, 0, 2, 3], dtype=int)')
b = np.array([-1, 1, 0, 2, 3], dtype=int)
print(b)
print('b.astype(float)')
print(b.astype(float))

print('divisao')
#print('a = a.astype(int)')
#a = a.astype(int)
b = b.astype(float)
print('a')
print(a)
print('b')
print(b)
print('comando: c = np.divide(a, b, out=np.zeros_like(a), where=b!=0)')
c = np.divide(a, b, out=np.zeros_like(a), where=b!=0)
print(c)

print('seleçao')
print('a = np.array([[0,1,1,0], [1,1,0,1], [0,1,0,1]], dtype=float)')
a = np.array([[0,1,1,0], [1,1,0,1], [0,1,0,1]], dtype=float)
print(a)
print('b = a[:,1:]')
b = a[:,1:]
print('b:')
print(b)
print('b = (a[:,:]==1.0).sum(axis=0)')
b = (a[:,:]==1.0).sum(axis=0)
print(b)
print('b = (a[:,:]==1).astype(float).sum(axis=0)')
b = (a[:,:]==1).astype(float).sum(axis=0)
print(b)
print('b = a.sum(axis=0)')
b = a.sum(axis=0)
print(b)
print('b = a.sum(axis=0, dtype=float)')
b = a.sum(axis=0, dtype=float)
print(b)


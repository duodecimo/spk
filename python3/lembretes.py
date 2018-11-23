#!/bin/python

import numpy as np

print("Alo, python!")
a=np.arange(6).reshape(2,3)
print('comando: a=np.arange(6).reshape(2,3)')
print(a)
print('shape de a: ', np.shape(a))
print('portanto: a[linhas, colunas]')
print('comando: a[:,:1]')
print(a[:,:1])
print('comando: a[:0,:1]')
print(a[:0,:1])
print('comando: a[1,1]')
print(a[1,1])

a=np.random.randint(2, size=(10, 8))
print('shape de a: ', np.shape(a))
l=np.shape(a)[0]
a[:,0] = np.random.randint(l/2,l-1,size=l)
print('a:')
print(a)


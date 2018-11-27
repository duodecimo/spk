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


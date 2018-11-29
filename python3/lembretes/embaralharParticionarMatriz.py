#!/bin/python
import sys
sys.path.append('/home/duo/anaconda3/lib/python3.6/site-packages')
import numpy as np

print("Alo, python!")
a=np.arange(60).reshape(20,3)
print('comando: a=np.arange(60).reshape(20,3)')
print(a)
print('shape de a: ', np.shape(a))
print('portanto: a[linhas, colunas]')
print('np.random.shuffle(a)')
np.random.shuffle(a)
print('l = a.shape[0]')
l = a.shape[0]
print('b, c, d = a[: int(l * .6)], x[int(l * .6) : int(l * .8)], x[int(l * .8):] ')
b, c, d = a[: int(l * .6)], a[int(l * .6) : int(l * .8)], a[int(l * .8):] 
print('b')
print(b)
print('c')
print(c)
print('d')
print(d)

#!/bin/python

import numpy as np

class No():
    def __init__(self):
        self.esquerda = None
        self.direita = None
        self.palavra = None
    def inserirPalavra(self, palavra):
        self.palavra = palavra
    def retornarPalavra(self):
        return self.palavra


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
print('np.delete(a, [3], axis=1):')
print(np.delete(a, [3], axis=1))
print('np.delete(a, [0], axis=1):')
print(np.delete(a, [0], axis=1))

no = No()
no.inserirPalavra("Alo, no!")
ret = no.retornarPalavra()
print(ret)

a = np.array([-1, 0, 1, 2, 3], dtype=float)
b = np.array([ 0, 0, 0, 2, 2], dtype=float)

# If you don't pass `out` the indices where (b == 0) will be uninitialized!
c = np.divide(a, b, out=np.zeros_like(a), where=b!=0)
print(a)
print('dividido por')
print(b)
print('igual a')
print(c)
print('errado?')
c=a/b
print(c.clip(min=0))
print(c)
c *= (c>0)
print(c)

a = np.array([-1, 2, -5, 9, -3], dtype=float)
print('a:')
print(a)
print('a.clip(min=0)')
print(a.clip(min=0))
a *= (a>0)
print(a)

#[ 0.   0.   0.   1.   1.5]

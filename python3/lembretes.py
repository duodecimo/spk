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

#!/bin/python

import numpy as np
from datetime import datetime

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
no.inserirPalavra("Alo, No!")
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

a = np.array([[1,2,3],[4,5,6]])
print('array sizes')
print(a)
print('No dims')
print(np.size(a))
print('dim 1')
print(np.size(a,1))
print('dim 0')
print(np.size(a,0))

comp = datetime.utcnow().strftime('%Y_%m_%d_%H_%M_%S_%f')[:-4] 
print('arq_' + comp + '.pkl')

x, y = 200,20
mensagens=np.random.randint(2, size=(x, y))
# primeira linha, respostas
mensagens[:,0] = np.random.randint(50, 900, size=x)

palavras=['resposta']
for i in range(np.size(mensagens, 1) -1):
    palavras.append('pal' + str(i+1))
print('palavras shape: ', np.shape(palavras))
print(palavras)
print('mensagens shape: ', np.shape(mensagens))
print(mensagens)

a = np.array([[1, 0, 0], [1, 0, 0], [2, 3, 4], [2, 5, 6]])
print('print(a)')
print(a)
print('print(np.size(a,0))')
print(np.size(a,0))
print('print(np.size(a,1))')
print(np.size(a,1))
print('print(a[:,0])')
print(a[:,0])
print(np.unique(a[:,0]))
print(np.unique(a[:,0]))
print(np.unique(a[:,0], 1))
a = np.array([[1, 0, 0], [1, 0, 2], [2, 3, 4]])
print(a)
print(np.unique(a[:,0]))
print(np.unique(a[:,0], 0))
print(np.unique(a[:,0], 1))
a = ['lista', 'de', 'palavras', 'sob', 'pop']
print(a)
print(a.pop(0))
print(a)
print(a.pop(0))
print(a)
print(a.pop(0))
print(a)
print(a.pop(0))
print(a)
print(a.pop(0))
a.append('de')
a.append('repente')
print(a)
print(a.pop(0))
a.append('mais')
a.append('palavras')
a.append('são')
a.append('acrescentadas')
print(a)
print(a.pop(0))
print(a)
print(a.pop(0))
print(a)
print(a.pop(0))
print(a)
print(a.pop(0))
print(a)
print(a.pop(0))
print(a)
print(a.pop(0))



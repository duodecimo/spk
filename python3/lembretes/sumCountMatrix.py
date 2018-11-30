#!/bin/python

import numpy as np
#import pandas as pd

a=np.arange(15).reshape(5,3)
a=np.random.randint(2, size=(10, 8))
# primeira linha, palavras
a[:,0] = np.random.randint(50, 55, size=10)
print(a)
linhas_a = np.size(a, 0)
print('linhas em a: ', linhas_a)
print('qmp1 = (a[:,1:]==1.0).sum(axis=0, dtype=float)')
qmp1 = (a[:,1:]==1.0).sum(axis=0, dtype=float)
print(qmp1)
print('qmp0 = (a[:,1:]==0.0).sum(axis=0, dtype=float)')
qmp0 = (a[:,1:]==0.0).sum(axis=0, dtype=float)
print(qmp0)
print('qmp1 = np.divide(qmp1, linhas_a, dtype=float)')
qmp1 = np.divide(qmp1, linhas_a, dtype=float)
print(qmp1)
print('qmp0 = np.divide(qmp0, linhas_a, dtype=float)')
qmp0 = np.divide(qmp0, linhas_a, dtype=float)
print(qmp0)

'''
df = pd.DataFrame(a, columns = ["Answer", "a", "b", "c", "d", "e", "f", "g"])

res = df.groupby("Answer").sum()

print('res')
print(res)
'''
unq, unq_inv = np.unique(a[:, 0], return_inverse=True)
out = np.zeros((len(unq), a.shape[1]), dtype=a.dtype)
out[:, 0] = unq
np.add.at(out[:, 1:], unq_inv, a[:, 1:])

print('out')
print(out)

print('np.divide(out[:, 1:], linhas_a, dtype=float)')
print(np.divide(out[:, 1:], linhas_a, dtype=float))

print('np.sum(np.power(np.divide(out[:, 1:], linhas_a, dtype=float), 2), axis=0)')
print(np.sum(np.power(np.divide(out[:, 1:], linhas_a, dtype=float), 2), axis=0))

print('e = 1 - np.sum(np.power(np.divide(out[:, 1:], linhas_a, dtype=float), 2), axis=0)')
e = 1 - np.sum(np.power(np.divide(out[:, 1:], linhas_a, dtype=float), 2), axis=0)
print('e')
print(e)

print('b = np.logical_not(a).astype(int)')
b = np.logical_not(a).astype(int)
b[:,0] = a[:,0]
print('a')
print(a)
print('b')
print(b)

unq, unq_inv = np.unique(b[:, 0], return_inverse=True)
out = np.zeros((len(unq), b.shape[1]), dtype=b.dtype)
out[:, 0] = unq
np.add.at(out[:, 1:], unq_inv, b[:, 1:])
print('f = 1 - np.sum(np.power(np.divide(out[:, 1:], linhas_a, dtype=float), 2), axis=0)')
f = 1 - np.sum(np.power(np.divide(out[:, 1:], linhas_a, dtype=float), 2), axis=0)
print('f')
print(f)

# sendo e o gini com 1, f o gini com 0
# para a media ponderada
print('g = np.column_stack((e,f))')
g = np.column_stack((e,f))
print('g')
print(g)
print('h = np.column_stack((qmp1,qmp0))')
h = np.column_stack((qmp1,qmp0))
print('h')
print(h)

i = np.average(g, axis=1, weights=h)
print(i)
print(0.95*0.3 + 0.87*0.7)
'''

c= np.unique(a[:, 0]) 

print('c')
print(c)


print('a = a[a[:,0].argsort()]')
a = a[a[:,0].argsort()]
print(a)


print('b = (a[:,1:] == 1).sum(axis=1)')
b = (a[:,1:] == 1).sum(axis=1)
print(b)


c, d = np.unique(a[:, 0], return_index = True) 

print(c)
print(d)

print('b = np.transpose(a)')
b = np.transpose(a)
print('b')
print(b)

print('(b[1:,:] == 1).sum(axis=0)')
print((b[1:,:]  == 1).sum(axis=0))

# resultado
    [115   1   0   0   1   0   0   0]
     [416   1   0   0   0   0   1   1]
     [677   1   0   1   1   0   1   1]
     [636   0   1   1   0   0   1   1]
     [840   1   1   0   1   1   1   0]
     [323   1   0   0   1   0   0   1]
     [242   1   0   1   1   1   1   1]
     [633   0   0   1   1   0   1   1]
     [373   0   0   1   1   0   0   1]]
    (a[:,1:] == 1).sum(axis=1)
    [2 2 3 5 4 5 3 6 4 3]
    b = np.transpose(a)
    b
    [[449 115 416 677 636 840 323 242 633 373]
     [  0   1   1   1   0   1   1   1   0   0]
     [  1   0   0   0   1   1   0   0   0   0]
     [  0   0   0   1   1   0   0   1   1   1]
     [  0   1   0   1   0   1   1   1   1   1]
     [  0   0   0   0   0   1   0   1   0   0]
     [  0   0   1   1   1   1   0   1   1   0]
     [  1   0   1   1   1   0   1   1   1   1]]
    (b[1:,:] == 1).sum(axis=0)
    [2 2 3 5 4 5 3 6 4 3]
'''


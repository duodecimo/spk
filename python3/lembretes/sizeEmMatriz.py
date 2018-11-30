#!/bin/python

import numpy as np

a = np.array([[1, 2, 3], [4, 5, 6]])
print('matriz a:')
print(a)
print('np.size(a) = ', np.size(a))
print('np.size(a,0)) = ', np.size(a,0))
print('np.size(a,1)) = ', np.size(a,1))

a = np.array([1, 2, 3])
print('vetor a:')
print(a)
print('np.size(a) = ', np.size(a))
try:
    print('np.size(a,0)) = ', np.size(a,0))
    print('np.size(a,1)) = ', np.size(a,1))
except Exception as ex:
    print('Erro: ', ex)

'''

matriz a:
[[1 2 3]
 [4 5 6]]
np.size(a) =  6
np.size(a,0)) =  2
np.size(a,1)) =  3
vetor a:
[1 2 3]
np.size(a) =  3
np.size(a,0)) =  3
Erro:  tuple index out of range

'''

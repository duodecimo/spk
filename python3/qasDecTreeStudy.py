#!/bin/python

import numpy as np
from timeit import default_timer as timer

start = timer()
m = np.random.randint(2, size=(17000, 3000))
#m = np.random.randint(2, size=(5, 3))
print('m:')
print(m)
s = (m==1).sum(axis=0)
print('sum: (where value = 1)')
print(s[:20])
indexes, values = np.nonzero(m[:1])
#x = np.array([[1, 2, 3], [1, 5, 6], [2,8,9], [1,11,12], [2,13,14], [3,15,16], [1, 3, 2]], np.int32)
#print('x:')
#print(x)
mi, mc = np.unique(m[:,0], return_counts=True)
mr = np.column_stack((mi,mc))
print('mr: (group)')
print(mr)

end = timer()
print('time running: ', end - start) # Time in seconds, e.g. 5.3809195240028




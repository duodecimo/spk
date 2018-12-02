#!/bin/python

import numpy as np

'''
a = np.array([[1, 0, 0], [1, 0, 0], [2, 3, 4]])
print('a:')
print(a)
print('a[:,0]')
print(a[:,0])
print('np.unique(a[:,0])')
print(np.unique(a[:,0]))
print('np.size(np.unique(a[:,0]))')
print(np.size(np.unique(a[:,0])))
'''


vet_sub_tot_resps = np.array([ 3,  2,  3, 2,  1,  1,  2,  3,  4,  1,  1,  6,  5,  1,  1,  1,  1,  3,  2,  1,  1,  1,  1,  2,  2,
                      5,  2,  1,  1, 11,  1,  2,  3, 14,  1,  1,  1,  1, 31,  2, 13,  1,  8,  1,  1,  1,  1,  2,  1,  1,
                      1,  1,  1,  3,  1,  3,  2,  1,  1,  2,  3,  8,  5,  1,  2,  1,  1,  1,  1,  4,  2,  1,  1,  2,  1,
                      1, 17,  1,  3,  8,  1,  2,  2,  2,  6,  5])
tot_resps = 256
sum_probs_resps = np.divide(vet_sub_tot_resps, tot_resps, dtype=float)
print(sum_probs_resps)
sum_probs_resps = vet_sub_tot_resps.astype(dtype=float) / tot_resps
print(sum_probs_resps)

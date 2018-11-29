#!/bin/python

import numpy as np

a = np.array([-1, 2, -5, 9, -3], dtype=float)
print('a:')
print(a)
print('a.clip(min=0)')
print(a.clip(min=0))
print('a *= (a>0)')
a *= (a>0)
print(a)


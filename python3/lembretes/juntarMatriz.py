import numpy as np

a = np.array([[1, 2, 3], [4, 5, 6]])
print('a:\n', a)
a = np.append(a, a, axis=0)
np.random.shuffle(a)
print('a:\n', a)

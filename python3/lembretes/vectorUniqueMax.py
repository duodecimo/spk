import numpy as np

a = np.arange(5, 8)
a[0] = a[2]
nd_respostas, contagem = np.unique(a, return_counts=True)
print('a')
print(a)
print('unique')
print(nd_respostas)
print('contagem')
print(contagem)
print('nd_respostas[np.argmin(contagem)]')
print(nd_respostas[np.argmin(contagem)])
print('nd_respostas[np.argmax(contagem)]')
print(nd_respostas[np.argmax(contagem)])

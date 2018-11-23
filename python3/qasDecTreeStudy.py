#!/bin/python

import numpy as np
import os
import csv
from timeit import default_timer as timer

start = timer()
#m = np.random.randint(2, size=(17000, 3000))
#m = np.random.randint(2, size=(5, 3))

#ler o arquivo csv
mensagens = []
with open("../../data/Training.csv", encoding='iso-8859-1') as csvfile:
    reader = csv.reader(csvfile)
    palavras = next(reader, None)
    for mensagem in reader:
        mensagens.append(mensagem)
mensagens = np.asarray(mensagens, dtype = np.dtype('uint32'))

print('Arquivo csv:')
print('mensagens: ', len(mensagens))
print('palavras: ', len(palavras))

s = (mensagens[:,1:]==1).sum(axis=0)
print('soma: (quando valor = 1)')
print(s[:20])
print('mensagens:')
print(mensagens)

respostas, contagem = np.unique(mensagens[:,0], return_counts=True)
respostas_agrupadas = np.column_stack((respostas,contagem))
print('respostas_agrupadas: (Respostas agrupadas)')
print(respostas_agrupadas[:, :])

end = timer()
print('time running: ', end - start) # Time in seconds, e.g. 5.3809195240028




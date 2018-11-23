#!/bin/python

import numpy as np
import os
import csv
from timeit import default_timer as timer


def criaNo(mensagens, palavras, no='raiz'):
    qMens = np.shape(mensagens)[0]
    print('')
    print('='*79)
    print('nó ', no, ' - quantidade de mensagens: ', qMens)
    print('='*79)

    # escolher uma resposta para iniciar o processo:
    #  a resposta com maior número de ocorrências.
    respostas, contagem = np.unique(mensagens[:,0], return_counts=True)
    respostasAgrupadas = np.column_stack((respostas,contagem))
    #  selecionar maior resposta agrupada
    respEsc = respostasAgrupadas[np.argmax(respostasAgrupadas[:,1:]), 0]
    print(' Reposta escolhida: ', respEsc);

    # calculando gini de O (O = conjunto de mensagens e suas respostas)
    respEscMensagens = mensagens[mensagens[:,0]==respEsc]
    print('conjunto de mensagens apenas com a resposta escolhida')
    print(respEscMensagens)
    qMensRespEsc = np.shape(respEscMensagens)[0]
    print('quantidade de mensagens com a resposta escolhida: ', qMensRespEsc)
    # taxa de mensagens com a resposta escolhida (C)
    tMensRespEsc = qMensRespEsc / qMens;
    print('taxa de mensagens com a resposta escolhida: ', tMensRespEsc);
    # taxa de mensagens sem a resposta escolhida (A)
    tMens_RespEsc = (qMens - qMensRespEsc) / qMens;
    print('taxa de mensagens sem a resposta escolhida: ', tMens_RespEsc);
    giniO = 1 - (pow(tMensRespEsc, 2) + pow(tMens_RespEsc, 2));
    # gini negativo não faz sentido ...
    giniO = max(0, giniO);
    print('GINI de O: ', giniO);
    # calculando o gini de cada palavra
    #  mensagens com cada palavra avaliada e qualquer resposta
    vqMensPalAval = (mensagens[:,1:]==1).sum(axis=0)
    print('mensagens com cada palavra avaliada e qualquer resposta:')
    print(vqMensPalAval)
    # quantidade de mensagens com a resposta escolhida com cada palavra
    vqMensRespEscPalAval = (respEscMensagens[:,1:]==1).sum(axis=0)
    print('mensagens com cada palavra e a resposta escolhida:')
    print(vqMensRespEscPalAval)
    # taxa de mensagens com a palavra sendo analisada e a resposta escolhida
    vtqMensRespEscPalAval = vqMensRespEscPalAval/vqMensPalAval
    print('taxa de mensagens com cada palavra e a resposta escolhida:')
    print(vtqMensRespEscPalAval)
    # taxa de mensagens com a palavra sendo analisada e a resposta diferente da escolhida
    vtqMens_RespEscPalAval = (vqMensPalAval - vqMensRespEscPalAval)/vqMensPalAval
    print('taxa de mensagens com cada palavra e resposta diferente da escolhida:')
    print(vtqMens_RespEscPalAval)
    # gini das mensagens com cada palavra e com a resposta escolhida
    vGiniMensPalRespEsc = 1 - (pow(vtqMensRespEscPalAval, 2) + pow(vtqMens_RespEscPalAval, 2));
    print('gini das mensagens com cada palavra e com a resposta escolhida:')
    print(vGiniMensPalRespEsc)

    #  mensagens sem cada palavra avaliada e qualquer resposta
    vqMens_PalAval = (mensagens[:,1:]==0).sum(axis=0)
    # quantidade de mensagens com a resposta escolhida sem cada palavra
    vqMensRespEsc_PalAval = (respEscMensagens[:,1:]==0).sum(axis=0)
    print('mensagens com a resposta escolhida e sem cada palavra:')
    print(vqMensRespEsc_PalAval)
    # taxa de mensagens sem a palavra sendo analisada e com resposta escolhida
    vtqMensRespEsc_PalAval = vqMensRespEscPalAval/vqMens_PalAval
    print('taxa de mensagens com a resposta escolhida e sem cada palavra:')
    print(vtqMensRespEsc_PalAval)
    # taxa de mensagens sem cada palavra sendo avaliada e resposta diferente da escolhida
    vtqMens_RespEsc_PalAval = (vqMens_PalAval - vqMensRespEsc_PalAval)/vqMens_PalAval
    print('taxa de mensagens sem cada palavra sendo avaliada e resposta diferente da escolhida:')
    print(vtqMens_RespEsc_PalAval)
    # gini das mensagens sem cada palavra sendo avaliada e sem a resposta escolhida
    vGiniMens_PalAval_RespEsc = 1 - (pow(vtqMensRespEsc_PalAval, 2) + pow(vtqMens_RespEsc_PalAval, 2));
    print('gini das mensagens sem cada palavra sendo avaliada e sem a resposta escolhida:')
    print(vGiniMens_PalAval_RespEsc)

    # calculando o gini de cada palavra
    vGiniPalAval = giniO - ((vGiniMensPalRespEsc * vqMensPalAval / qMens) + (vGiniMens_PalAval_RespEsc * vqMens_PalAval / qMens))
    print('Gini de cada palavra avaliada:')
    print(vGiniPalAval)

    # melhor palavra: a palavra com o maior GINI
    PalEsc = palavras[np.argmax(vGiniPalAval) +1]
    print('Melhor palavra: ', PalEsc);
    


inicio = timer()

mensagens = []

#ler o arquivo csv


with open("../../data/Training.csv", encoding='iso-8859-1') as csvfile:
    reader = csv.reader(csvfile)
    palavras = next(reader, None)
    for mensagem in reader:
        mensagens.append(mensagem)
mensagens = np.asarray(mensagens, dtype = np.dtype('uint32'))

# ou, para testes
'''
mensagens=np.random.randint(2, size=(10, 8))
mensagens[:,0] = np.random.randint(5,9,size=10)
palavras=('resposta','a', 'b', 'c', 'd', 'e', 'f', 'g')
'''

print('Arquivo csv:')
print('mensagens: ', len(mensagens))
print('palavras: ', len(palavras))

s = (mensagens[:,1:]==1).sum(axis=0)
print('soma: (quando valor = 1)')
print(s[:20])
print('mensagens:')
print(mensagens)

criaNo(mensagens, palavras)

fim = timer()
print('tempo de execução (em segundos): ', fim - inicio) # Time in seconds, e.g. 5.3809195240028



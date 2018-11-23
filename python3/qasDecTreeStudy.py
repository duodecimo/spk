#!/bin/python

import numpy as np
import os
import csv
from timeit import default_timer as timer

class No():
    def __init__(self):
        self.esquerda = None
        self.direita = None
        self.palavra = None
        self.resposta = None
    def inserirEsquerda(self, no):
        self.esquerda = no
    def inserirDireita(self, no):
        self.direita = no
    def inserirPalavra(self, palavra):
        self.palavra = palavra
    def retornarPalavra(self):
        return self.palavra
    def inserirResposta(self, resposta):
        self.resposta = resposta
    def retornarResposta(self):
        return self.resposta

def dividir(x, y):
    if y==0: return 0
    return x/y

def criaNo(mensagens, palavras, no, noNome='raiz'):
    global inicio
    global debug

    fim = timer()
    print('='*79)
    print('')
    print('Ate o no ', noNome, ': ')
    print(' tempo (em segundos): ', fim - inicio) # Time in seconds, e.g. 5.3809195240028

    qMens = np.shape(mensagens)[0]
    print('quantidade de mensagens: ', qMens)
    print('='*79)

    # escolher uma resposta para iniciar o processo:
    #  a resposta com maior número de ocorrências.
    respostas, contagem = np.unique(mensagens[:,0], return_counts=True)
    respostasAgrupadas = np.column_stack((respostas,contagem))
    #  selecionar maior resposta agrupada
    respEsc = respostasAgrupadas[np.argmax(respostasAgrupadas[:,1:]), 0]
    if debug: print(' Reposta escolhida: ', respEsc);

    # calculando gini de O (O = conjunto de mensagens e suas respostas)
    respEscMensagens = mensagens[mensagens[:,0]==respEsc]
    if debug: print('conjunto de mensagens apenas com a resposta escolhida')
    if debug: print(respEscMensagens)
    qMensRespEsc = np.shape(respEscMensagens)[0]
    if debug: print('quantidade de mensagens com a resposta escolhida: ', qMensRespEsc)
    # taxa de mensagens com a resposta escolhida (C)
    tMensRespEsc = dividir(qMensRespEsc, qMens);
    if debug: print('taxa de mensagens com a resposta escolhida: ', tMensRespEsc);
    # taxa de mensagens sem a resposta escolhida (A)
    tMens_RespEsc = dividir((qMens - qMensRespEsc), qMens);
    if debug: print('taxa de mensagens sem a resposta escolhida: ', tMens_RespEsc);
    giniO = 1 - (pow(tMensRespEsc, 2) + pow(tMens_RespEsc, 2));
    # gini negativo não faz sentido ...
    giniO = max(0, giniO);
    if debug: print('GINI de O: ', giniO);
    # calculando o gini de cada palavra
    #  mensagens com cada palavra avaliada e qualquer resposta
    vqMensPalAval = (mensagens[:,1:]==1).sum(axis=0)
    if debug: print('mensagens com cada palavra avaliada e qualquer resposta:')
    if debug: print(vqMensPalAval)
    # quantidade de mensagens com a resposta escolhida com cada palavra
    vqMensRespEscPalAval = (respEscMensagens[:,1:]==1).sum(axis=0)
    if debug: print('mensagens com cada palavra e a resposta escolhida:')
    if debug: print(vqMensRespEscPalAval)
    # taxa de mensagens com a palavra sendo analisada e a resposta escolhida
    vtqMensRespEscPalAval = np.divide(vqMensRespEscPalAval, vqMensPalAval, out=np.zeros_like(vqMensRespEscPalAval), where=vqMensPalAval!=0, casting='unsafe')
    if debug: print('taxa de mensagens com cada palavra e a resposta escolhida:')
    if debug: print(vtqMensRespEscPalAval)
    # taxa de mensagens com a palavra sendo analisada e a resposta diferente da escolhida
    vqMens_RespEscPalAval = vqMensPalAval - vqMensRespEscPalAval
    vtqMens_RespEscPalAval = np.divide(vqMens_RespEscPalAval, vqMensPalAval, out=np.zeros_like(vqMens_RespEscPalAval), where=vqMensPalAval!=0, casting='unsafe')
    if debug: print('taxa de mensagens com cada palavra e resposta diferente da escolhida:')
    if debug: print(vtqMens_RespEscPalAval)
    # gini das mensagens com cada palavra e com a resposta escolhida
    vGiniMensPalRespEsc = 1 - (pow(vtqMensRespEscPalAval, 2) + pow(vtqMens_RespEscPalAval, 2));
    # gini negativo não faz sentido, zera
    vGiniMensPalRespEsc = vGiniMensPalRespEsc.clip(min=0)
    if debug: print('gini das mensagens com cada palavra e com a resposta escolhida:')
    if debug: print(vGiniMensPalRespEsc)

    #  mensagens sem cada palavra avaliada e qualquer resposta
    vqMens_PalAval = (mensagens[:,1:]==0).sum(axis=0)
    # quantidade de mensagens com a resposta escolhida sem cada palavra
    vqMensRespEsc_PalAval = (respEscMensagens[:,1:]==0).sum(axis=0)
    if debug: print('mensagens com a resposta escolhida e sem cada palavra:')
    if debug: print(vqMensRespEsc_PalAval)
    # taxa de mensagens sem a palavra sendo analisada e com resposta escolhida
    vtqMensRespEsc_PalAval = np.divide(vqMensRespEsc_PalAval, vqMens_PalAval, out=np.zeros_like(vqMensRespEsc_PalAval), where=vqMens_PalAval!=0, casting='unsafe')
    if debug: print('taxa de mensagens com a resposta escolhida e sem cada palavra:')
    if debug: print(vtqMensRespEsc_PalAval)
    # taxa de mensagens sem cada palavra sendo avaliada e resposta diferente da escolhida
    vqMens_RespEsc_PalAval = vqMens_PalAval - vqMensRespEsc_PalAval
    vtqMens_RespEsc_PalAval = np.divide(vqMens_RespEsc_PalAval, vqMens_PalAval, out=np.zeros_like(vqMens_RespEsc_PalAval), where=vqMens_PalAval!=0, casting='unsafe')
    if debug: print('taxa de mensagens sem cada palavra sendo avaliada e resposta diferente da escolhida:')
    if debug: print(vtqMens_RespEsc_PalAval)
    # gini das mensagens sem cada palavra sendo avaliada e sem a resposta escolhida
    vGiniMens_PalAval_RespEsc = 1 - (pow(vtqMensRespEsc_PalAval, 2) + pow(vtqMens_RespEsc_PalAval, 2));
    # gini negativo não faz sentido, zera
    vGiniMens_PalAval_RespEsc = vGiniMens_PalAval_RespEsc.clip(min=0)
    if debug: print('gini das mensagens sem cada palavra sendo avaliada e sem a resposta escolhida:')
    if debug: print(vGiniMens_PalAval_RespEsc)

    # calculando o gini de cada palavra
    vGiniPalAval = giniO - ((vGiniMensPalRespEsc * vqMensPalAval / qMens) + (vGiniMens_PalAval_RespEsc * vqMens_PalAval / qMens))
    # gini negativo não faz sentido, zera
    vGiniPalAval = vGiniPalAval.clip(min=0)
    if debug: print('Gini de cada palavra avaliada:')
    if debug: print(vGiniPalAval)

    # melhor palavra: a palavra com o maior GINI
    indPalEsc = np.argmax(vGiniPalAval)
    PalEsc = palavras[indPalEsc +1]
    if debug: print('Melhor palavra: ', PalEsc, ' indice: ', indPalEsc +1)
    no.inserirPalavra(PalEsc)
    if debug: print('conferindo palavra do no: ', no.retornarPalavra())
    # dividir as mensagens entre as que contém a palavra com melhor GINI e as que não.
    mensagensPalAval = mensagens[mensagens[:, indPalEsc+1]==1]
    mensagens_PalAval = mensagens[mensagens[:, indPalEsc+1]==0]
    if debug: print('mensagens que contém a melhor palavra:')
    if debug: print(mensagensPalAval)
    if debug: print('mensagens sem a melhor palavra:')
    if debug: print(mensagens_PalAval)
    # remove a palavra deste nó
    mensagensPalAval = np.delete(mensagensPalAval, [indPalEsc+1], axis=1)
    mensagens_PalAval = np.delete(mensagens_PalAval, [indPalEsc+1], axis=1)
    palavrasProxNo = np.delete(palavras, [indPalEsc+1])
    if debug: print('palavras proximo no:')
    if debug: print(palavrasProxNo)
    # verifica a expansão da árvore
    noEsq = No() # folhas naõ terão palavras!
    noDir = No()
    no.inserirEsquerda(noEsq)
    no.inserirDireita(noDir)
    #  print('repostas ', len(np.unique(mensagensPalAval[:,0])))
    #  print(np.unique(mensagensPalAval[:,0]))
    noEsqResp = np.unique(mensagensPalAval[:,0])
    # a primeira coluna tem as respostas, plavras começam a partir da segunda coluna
    # portanto, mensagens com uma unica resposta possuem pelo menos dois elementos
    if len(noEsqResp) == 2:
        # resta apenas uma resposta, é um nó folha!
        noEsq.inserirResposta(noEsqResp[0])
        if debug: print('folha com resposta unica: ', noEsqResp[0], ' a esquerda do no ', noNome)
    elif len(np.unique(mensagensPalAval[:,0])) <= 1:
        # não existe resposta ou esgotaram-se as palavras sem atingir uma única resposta
        # (teria sido capturado acima)
        # É uma folha sem decisão de resposta
        if debug: print('folha vazia a esquerda do no ', noNome)
    else:
        # se chegou aqui, existe no esquerdo
        # chama recursivamente
        criaNo(mensagensPalAval, palavrasProxNo, noEsq, noNome + ".L")
    noDirResp = np.unique(mensagens_PalAval[:,0])
    # a primeira coluna tem as respostas, plavras começam a partir da segunda coluna
    # portanto, mensagens com uma unica resposta possuem pelo menos dois elementos
    if len(noDirResp) == 2:
        # resta apenas uma resposta, é um nó folha!
        noDir.inserirResposta(noDirResp[0])
        if debug: print('folha com resposta unica: ', noDirResp[0], ' a direita do no ', noNome)
    elif len(np.unique(mensagens_PalAval[:,0])) <= 1:
        # não existe resposta ou esgotaram-se as palavras sem atingir uma única resposta
        # (teria sido capturado acima)
        # É uma folha sem decisão de resposta
        if debug: print('folha vazia a direita do no ', noNome)
    else:
        # se chegou aqui, existe no esquerdo
        # chama recursivamente
        criaNo(mensagens_PalAval, palavrasProxNo, noDir, noNome + ".R")



inicio = timer()

debug = False

mensagens = []

#ler o arquivo csv

'''
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


print('Arquivo csv:')
print('mensagens: ', len(mensagens))
print('palavras: ', len(palavras))

s = (mensagens[:,1:]==1).sum(axis=0)
print('soma: (quando valor = 1)')
print(s[:20])
print('mensagens:')
print(mensagens)

arvore = No()

criaNo(mensagens, palavras, arvore)

fim = timer()
print('tempo de execução (em segundos): ', fim - inicio) # Time in seconds, e.g. 5.3809195240028



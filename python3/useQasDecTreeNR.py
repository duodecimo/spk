#!/bin/python

import numpy as np
import os
import csv
from timeit import default_timer as timer
import os
import psutil
import sys
import pickle
import itertools
from datetime import datetime
from datetime import timedelta
from multiprocessing.dummy import Pool as ThreadPool
import pathlib
#globais
debug = False
executarTeste = False
tamTeste = [500,60]
paralelizar = False
numMaxNosPar = 1000
inicio = timer()
pid = os.getpid()
py = psutil.Process(pid)
qmaxmens = 0
qtotmenscalc = 0
limitePersArv = 100000
caminhoDePersistencia = '.'
# valor recomendado 5.0
intervaloMostra = 5.0

class No(): # é o objeto do dicionário árvore
    def __init__(self, noDados): # recebe como parâmetro um noDados, de onde extrai todos seus atributos
        self.palavra = noDados.retPalavra() # utilizada para dividir a árvore, pode não existir em folhas
        self.respostas = noDados.retRespostas()
        self.folha = noDados.eFolha()
    def Palavra(self):
        return self.palavra
    def Respostas(self):
        return self.respostas
    def eFolha(self):
        return self.folha


def CarregarArvore(nomeArq):
    arq = open(nomeArq,'rb')
    arvore = pickle.load(arq)
    arq.close()
    return arvore

def main():
    global executarTeste
    global debug
    global inicio
    global py
    global qmaxmens
    global limitePersArv
    global caminhoDePersistencia
    global intervaloMostra
    global numMaxNosPar
    global tamTeste

    # conjunto de mensagens
    mensagens = []
    # conjunto de treino
    treino = []
    # conjunto de testes
    testes = []
    
    if executarTeste:
        intervaloMostra = 0.00005
        # gerar treino randomico, para testes
        # x, y = 40,20
        mensagens=np.random.randint(2, size=(tamTeste[0], tamTeste[1]))
        # primeira linha, palavras
        mensagens[:,0] = np.random.randint(50, 900, size=tamTeste[0])
        palavras=['resposta']
        for i in range(np.size(mensagens, 1) -1):
            palavras.append('pal' + str(i+1))
        print('Teste aleatório:')
    else:
        #ler o arquivo csv
        with open("../../data/Training.csv", encoding='iso-8859-1') as csvfile:
            reader = csv.reader(csvfile)
            palavras = next(reader, None)
            for mensagem in reader:
                mensagens.append(mensagem)
        mensagens = np.asarray(mensagens, dtype = np.dtype('uint32'))
        print('Arquivo csv:')

    # para particionar matriz
    # treino = 90%
    # teste = 10%
    np.random.shuffle(a)
    l = mensagens.shape[0]
    # b, c, d = a[: int(l * .6)], a[int(l * .6) : int(l * .8)], a[int(l * .8):]
    treino, teste = mensagens[: int(l * .9)], mensagens[int(l * .9) :]

    totMensO = len(mensagens)
    print('mensagens: ', len(mensagens))
    print('palavras: ', len(palavras))

    print('mensagens:')
    print(mensagens)
    s = (mensagens[:,1:]==1).sum(axis=0, dtype=float)
    print('soma: (algumas a partir da segunda coluna, valores = 1)')
    print(s[:20])
    
    # caminho para recuperar a arvore
    #cole o arquivo aqui
    caminhoDePersistencia = '/extra2/mySpark/javaNetbeans/arvorespklarmazenadas/grupo2018_11_27_12_22_12_87/' \
     + 'arvore_2018_11_27_12_24_08_2580.pkl'

    # ler arvore
    arvore = CarregarArvore(caminhoDePersistencia)
    print('arvore carregada, tamanho: ', len(arvore))
    acertos = 0
    erros = 0
    testadas = 0
    # quantidade de mensagens a testar
    qMensTeste = np.size(mensagens, 0)
    print('mensagens no conjunto de mensagens: ', qMensTeste)
    for i in range(qMensTeste):
        mensagem = mensagens[i]
        #pesquisar a arvore gerada iniciando pela raiz
        proximo = [0]
        while(len(proximo)>0):
            ind = proximo.pop(0)
            no = arvore.get(ind)
            if debug: print('no: ', ind)
            if not no.eFolha():
                # verifica se a mensagem tem a
                # palavra da arvore ou não.
                palNo = no.Palavra()
                if mensagem[palavras.index(palNo)] == 1:
                    # mensagem tem a palavra
                    # vai para a esquerda
                    proximo.append(ind*2+1)
                else:
                    # mensagem não tem a palavra
                    # vai para a direita
                    proximo.append(ind*2+2)
            else:
                # hora da decisão
                if mensagem[0] == no.Respostas()[0]:
                    acertos +=1
                else:
                    erros += 1
                testadas += 1
                print('testadas: ', testadas, ' acertos: ', acertos, ' erros:', erros)
                print('acuidade: ', acertos*100/testadas)
                # parte para a proxima pesquisa

    # em 28/11/2018
    # usando para teste o mesmo arquivo usado para treino:
    # testadas:  11719  acertos:  11717  erros: 2
    # acuidade:  99.98293369741445
    # ###############################################################################
    # Tempo de processamento:  0:01:07.919263
    # ###############################################################################

    fim = timer()
    print('#'*79)
    print('Tempo de processamento: ', str(timedelta(seconds=fim - inicio)))
    print('#'*79)

if __name__ == "__main__":
    main()


#!/bin/python

import numpy as np
import os
import csv
from timeit import default_timer as timer
import os
import psutil
import sys
import pickle
from datetime import datetime
from multiprocessing.dummy import Pool as ThreadPool

#globais
inicio = timer()
debug = True
pid = os.getpid()
py = psutil.Process(pid)


class NoDados(): # possui atributos para processar e gerar o no da arvore
    def __init__(self, indice, palavras, mensagens):
        self.indice = indice # vai ser o indice do dicionario arvore
        self.palavra = None # a melhor palavra que divide os nós
        self.respostas = None # uma lista de respostas, para os nós folha, idealmente apenas uma resposta
        self.mensagens = mensagens # matriz de mensagens a serem processadas
        self.palavras = palavras # vetor de palavras a serem processadas
        self.folha = False # indica se um nó é ou não folha

    def retIndice(self):
        return self.indice
    def insPalavra(self, palavra):
        self.palavra = palavra
    def retPalavra(self):
        return self.palavra
    def insRespostas(self, respostas):
        self.respostas = respostas
    def retRespostas(self):
        return self.respostas
    def insMensagens(self, mensagens):
        self.mensagens = mensagens
    def retMensagens(self):
        return self.mensagens
    def retPalavras(self):
        return self.palavras
    def atribFolha(self, val):
        self.folha = val
    def eFolha(self):
        return self.folha

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

def ProcessadorDeNosDados():
    def __init__(self, noDados):
        self.noDados = noDados
    def tarefaDeCalcular(self):
        global arvore
        global filaDeNos
        # Processa o noDados
        (noDadosEsq, noDadosDir) = calculaNo(noDados)
        # coloca na fila de nós a calcular
        filaDeNos.append(noDadosEsq)
        filaDeNos.append(noDadosDir)
        # coloca o nó calculado na árvore
        arvore[noDados.retIndice()] = No(noDados)      


def dividir(x, y):
    if y==0: return 0
    return x/y

def salvarArvore(arvore):
    comp = datetime.now().strftime('%Y_%m_%d_%H_%M_%S_%f')[:-2] 
    nomeArq = 'arvore_' + comp + '.pkl'
    arq = open(nomeArq,'wb')
    pickle.dump(arvore, arq, pickle.HIGHEST_PROTOCOL)
    arq.close()
    return nomeArq

def CarregarArvore(nomeArq):
    arq = open(nomeArq,'rb')
    arvore = pickle.load(arq)
    arq.close()
    return arvore

def calculaNo(noDados):
    global inicio
    global debug
    global py

    indice = noDados.retIndice()
    palavras = noDados.retPalavras();
    mensagens = noDados.retMensagens();

    fim = timer()
    print('='*79)
    usoMemoria = py.memory_info()[0]/2.**30  # memory use in GB...I think
    print('uso de memoria:', usoMemoria)

    print('')
    print('Ate o no ', indice, ': ')
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
    # inserir nos dados do nó a palavra que divide a árvore
    noDados.insPalavra(PalEsc)
    if debug: print('Melhor palavra: ', PalEsc, ' indice: ', indPalEsc +1)
    if debug: print('conferindo palavra do no: ', noDados.retPalavra())
    # dividir as mensagens entre as que contém a palavra com melhor GINI e as que não.
    mensagensPalAval = mensagens[mensagens[:, indPalEsc+1]==1]
    mensagens_PalAval = mensagens[mensagens[:, indPalEsc+1]==0]
    if debug: print('mensagens que contém a melhor palavra:')
    if debug: print(mensagensPalAval)
    if debug: print('mensagens sem a melhor palavra:')
    if debug: print(mensagens_PalAval)
    # remove a palavra dos novos conjuntos de mensagens (esquerdo e direito)
    mensagensPalAval = np.delete(mensagensPalAval, [indPalEsc+1], axis=1)
    mensagens_PalAval = np.delete(mensagens_PalAval, [indPalEsc+1], axis=1)
    # ajusta a lista de palavras para os nós filhos (esquerdo e direito)
    palavrasProxNo = np.delete(palavras, [indPalEsc+1])
    if debug: print('palavras proximo no:')
    if debug: print(palavrasProxNo)
    # inicia dados de nós de retorno
    # NoDados(indice, palavras, mensagens)
    noDadosEsq = NoDados(2*indice+1, palavrasProxNo, mensagensPalAval)
    noDadosDir = NoDados(2*indice+2, palavrasProxNo, mensagens_PalAval)
    # verifica a expansão da árvore:
    # caso não hajam mais mensagens, ou caso só fique uma resposta,
    # para de expandir
    # à esquerda
    
    # primeiro preciso verificar se há menos que duas respostas,
    # melhor agrupar os dados pelas respostas (primeira coluna) 
    # e verificar se há menos de duas linhas, caso sim,
    # é folha!
    # segundo preciso verificar o numero de linhas de mensagens,
    # se houver menos que duas mensagens é folha!
    # melhor usar a dimensão 1 de matriz para isso ...
    qMensE = np.size(mensagensPalAval,0)
    noDadosEsqResp = np.unique(mensagensPalAval[:,0])
    # a primeira coluna tem as respostas, as palavras começam a partir da segunda coluna
    # portanto, mensagens com uma unica resposta possuem pelo menos dois elementos
    if len(noDadosEsqResp) < 2 or qMensE <2:
        # len(noDadosEsqResp):
        #  se for 2, resta apenas uma resposta, é um nó folha!
        #  se menor, não existem respostas ou esgotaram-se as palavras sem atingir uma única resposta
        #  É uma folha sem decisão de resposta
        # qMensE <2:
        # quantidade de mensagens na partição.
        # se for < 2 não há mais o que quebrar, é uma folha!
        noDadosEsq.atribFolha(True)
        # sempre e só colocar respostas em nós folha
        noDadosEsq.insRespostas(noDadosEsqResp)
        if debug: print('folha com resposta(s) unica: ', noDadosEsqResp, ' a esquerda do no ', indice)
    # à direita
    qMensD = np.size(mensagens_PalAval, 0)
    noDadosDirResp = np.unique(mensagens_PalAval[:,0])
    # a primeira coluna tem as respostas, as palavras começam a partir da segunda coluna
    # portanto, mensagens com uma unica resposta possuem pelo menos dois elementos
    if len(noDadosDirResp) < 2 or qMensD <2:
        # len(noDadosDirResp):
        #  se for 2, resta apenas uma resposta, é um nó folha!
        #  se menor, não existem respostas ou esgotaram-se as palavras sem atingir uma única resposta
        #  É uma folha sem decisão de resposta
        # qMensD <2:
        # quantidade de mensagens na partição.
        # se for < 2 não há mais o que quebrar, é uma folha!
        noDadosDir.atribFolha(True)
        # só colocar respostas em nós folha
        noDadosDir.insRespostas(noDadosDirResp)
        if debug: print('folha com resposta(s): ', noDadosDirResp, ' a direita do no ', indice)

    return (noDadosEsq, noDadosDir)  


def main():

    # a arvore é um dicionário
    arvore = {}
    # uma lista de nós a serem processados
    filaDeNos = []
    # o primeiro noDados é pré processado,
    # por exemplo, recebe indice 0 (raiz).
    # os próximos são gerados no calculo do noDados,
    # o indice é calculado usando a formula
    # indice esquerda = 2* indice atual + 1
    # indice direita = 2* indice atual + 2

    # conjunto de treino
    mensagens = []

    #ler o arquivo csv

    '''
    with open("../../data/Training.csv", encoding='iso-8859-1') as csvfile:
        reader = csv.reader(csvfile)
        palavras = next(reader, None)
        for mensagem in reader:
            mensagens.append(mensagem)
    mensagens = np.asarray(mensagens, dtype = np.dtype('uint32'))

    '''

    # ou gerar treino randomico, para testes
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

    # dados do nó raiz
    #noDados = NoDados(indice, palavras, mensagens)
    noDados = NoDados(0, palavras, mensagens)
    pool = ThreadPool(4)
    while True:
        #(noDadosEsq, noDadosDir) = calculaNo(noDados)
        ## coloca na fila de nós a calcular
        #filaDeNos.append(noDadosEsq)
        #filaDeNos.append(noDadosDir)
        ## coloca o nó calculado na árvore
        #arvore[noDados.retIndice()] = No(noDados)
        #if debug: print('inserido na arvore indice: ', noDados.retIndice())
        # retira nó não calculado da fila
        pool.map(ProcessadorDeNosDados, noDados)

        try:
            while True: # enquanto não conseguir noDados para calcular
                noDados = filaDeNos.pop(0)
                # se for folha, não deve ser calculado
                # deve ser colocado na árvore e mais
                # um noDado deve ser retirado da fila
                if noDados.eFolha():
                    arvore[noDados.retIndice()] = No(noDados)
                else:
                    break
        except (ValueError, IndexError) as erro :
            # a arvore esta provávelmente vazia, fim de processamento
            # obs: quando usar threads, é preciso verificar
            # se ainda existem threads em execuçao, que podem
            # acrescentar novos nós a fila!
            break

    if debug:
        #percorrer a arvore gerada
        print('Percorrendo a arvore gerada')
        visitas = 0
        proximo = [0]
        while(len(proximo)>0):
            ind = proximo.pop(0)
            no = arvore.get(ind)
            print('no: ', ind)
            if not no.eFolha():
                proximo.append(ind*2+1)
                proximo.append(ind*2+2)
                print('  palavra  : ', no.Palavra())
            else:
                print('  respostas: ', no.Respostas())
        #salvar arvore
        nomeArq = salvarArvore(arvore)
        print('arvore salva no arquivo: ', nomeArq)
        # ler arvore
        arvore = CarregarArvore(nomeArq)
        print('Percorrendo a arvore recuperada')
        visitas = 0
        proximo = [0]
        while(len(proximo)>0):
            ind = proximo.pop(0)
            no = arvore.get(ind)
            print('no: ', ind)
            if not no.eFolha():
                proximo.append(ind*2+1)
                proximo.append(ind*2+2)
                print('  palavra  : ', no.Palavra())
            else:
                print('  respostas: ', no.Respostas())

    salvarArvore(arvore)
    fim = timer()
    print('tempo de execução (em segundos): ', fim - inicio) # Time in seconds, e.g. 5.3809195240028

if __name__ == "__main__":
    main()


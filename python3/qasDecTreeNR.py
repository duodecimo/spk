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
    global caminhoDePersistencia
    comp = datetime.now().strftime('%Y_%m_%d_%H_%M_%S_%f')[:-2] 
    nomeArq =  caminhoDePersistencia + 'arvore_' + comp + '.pkl'
    arq = open(nomeArq,'wb')
    pickle.dump(arvore, arq, pickle.HIGHEST_PROTOCOL)
    arq.close()
    return nomeArq

def CarregarArvore(nomeArq):
    arq = open(nomeArq,'rb')
    arvore = pickle.load(arq)
    arq.close()
    return arvore

def dividirArvore(arvore):
    n = len(arvore) // 2
    i = iter(arvore.items())      # alternatively, i = d.iteritems() works in Python 2

    arvore1 = dict(itertools.islice(i, n))   # grab first n items
    arvore2 = dict(i)                        # grab the rest

    return arvore1, arvore2


def calculaNo(noDados):
    global inicio
    global debug
    global py
    global qmaxmens
    global qtotmenscalc

    indice = noDados.retIndice()
    palavras = noDados.retPalavras();
    mensagens = noDados.retMensagens();

    fim = timer()
    qMens = np.shape(mensagens)[0]
    if qMens > qmaxmens:
        qmaxmens = qMens

    if debug:
        print('-'*79)
        usoMemoria = py.memory_info()[0]/2.**30  # memory use in GB...I think
        print('uso de memoria:', usoMemoria)
        print('')
        print('Ate o no ', indice, ': ')
        print(' tempo (em segundos): ', str(timedelta(seconds=fim - inicio)))
        print('quantidade de mensagens: ', qMens)
        print('-'*79)

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
    vqMensPalAval = (mensagens[:,1:]==1.0).sum(axis=0, dtype=float)
    if debug: print('mensagens com cada palavra avaliada e qualquer resposta:')
    if debug: print(vqMensPalAval)
    # quantidade de mensagens com a resposta escolhida com cada palavra
    vqMensRespEscPalAval = (respEscMensagens[:,1:]==1.0).sum(axis=0, dtype=float)
    if debug: print('mensagens com cada palavra e a resposta escolhida:')
    if debug: print(vqMensRespEscPalAval)
    # taxa de mensagens com a palavra sendo analisada e a resposta escolhida
    #
    # pode ser usado o método np.divide(), por exemplo:
    #  comando a = np.array([-1, 0, 1, 2, 3], dtype=float)
    #  resulta em a = [-1.  0.  1.  2.  3.]
    #  comando b = np.array([ 0, 0, 0, 2, 2], dtype=float)
    #  resulta em b = [ 0.  0.  0.  2.  2.]
    #  então, comando c = np.divide(a, b, out=np.zeros_like(a), where=b!=0)
    #  resulta em [ 0.   0.   0.   1.   1.5]
    #
    #  observe que comando c=a/b gera avisos:
    #    RuntimeWarning: divide by zero encountered in true_divide
    #    c=a/b
    #    RuntimeWarning: invalid value encountered in true_divide
    #    c=a/b
    vtqMensRespEscPalAval = \
    np.divide(vqMensRespEscPalAval, vqMensPalAval, out=np.zeros_like(vqMensRespEscPalAval), \
    where=vqMensPalAval!=0.0, casting='unsafe')
    if debug: print('taxa de mensagens com cada palavra e a resposta escolhida:')
    if debug: print(vtqMensRespEscPalAval)
    # taxa de mensagens com a palavra sendo analisada e a resposta diferente da escolhida
    vqMens_RespEscPalAval = vqMensPalAval - vqMensRespEscPalAval
    vtqMens_RespEscPalAval = \
    np.divide(vqMens_RespEscPalAval, vqMensPalAval, out=np.zeros_like(vqMens_RespEscPalAval), \
    where=vqMensPalAval!=0.0, casting='unsafe')
    if debug: print('taxa de mensagens com cada palavra e resposta diferente da escolhida:')
    if debug: print(vtqMens_RespEscPalAval)
    # gini das mensagens com cada palavra e com a resposta escolhida
    vGiniMensPalRespEsc = 1 - (pow(vtqMensRespEscPalAval, 2) + pow(vtqMens_RespEscPalAval, 2));
    # gini negativo não faz sentido, zera
    # pode ser utilizado o método clip, exemplo:
    # a: [-1.  2. -5.  9. -3.]
    # a.clip(min=0)
    # [ 0.  2.  0.  9.  0.]
    # no entanto:
    # a *= (a>0)
    # [-0.  2. -0.  9. -0.]
    vGiniMensPalRespEsc = vGiniMensPalRespEsc.clip(min=0)
    if debug: print('gini das mensagens com cada palavra e com a resposta escolhida:')
    if debug: print(vGiniMensPalRespEsc)

    #  mensagens sem cada palavra avaliada e qualquer resposta
    vqMens_PalAval = (mensagens[:,1:]==0).sum(axis=0, dtype=float)
    # quantidade de mensagens com a resposta escolhida sem cada palavra
    vqMensRespEsc_PalAval = (respEscMensagens[:,1:]==0).sum(axis=0, dtype=float)
    if debug: print('mensagens com a resposta escolhida e sem cada palavra:')
    if debug: print(vqMensRespEsc_PalAval)
    # taxa de mensagens sem a palavra sendo analisada e com resposta escolhida
    vtqMensRespEsc_PalAval = np.divide(vqMensRespEsc_PalAval, vqMens_PalAval, \
     out=np.zeros_like(vqMensRespEsc_PalAval), where=vqMens_PalAval!=0, casting='unsafe')
    if debug: print('taxa de mensagens com a resposta escolhida e sem cada palavra:')
    if debug: print(vtqMensRespEsc_PalAval)
    # taxa de mensagens sem cada palavra sendo avaliada e resposta diferente da escolhida
    vqMens_RespEsc_PalAval = vqMens_PalAval - vqMensRespEsc_PalAval
    vtqMens_RespEsc_PalAval = np.divide(vqMens_RespEsc_PalAval, vqMens_PalAval, \
     out=np.zeros_like(vqMens_RespEsc_PalAval), where=vqMens_PalAval!=0, casting='unsafe')
    if debug: print('taxa de mensagens sem cada palavra sendo avaliada e resposta diferente da escolhida:')
    if debug: print(vtqMens_RespEsc_PalAval)
    # gini das mensagens sem cada palavra sendo avaliada e sem a resposta escolhida
    vGiniMens_PalAval_RespEsc = 1 - (pow(vtqMensRespEsc_PalAval, 2) + pow(vtqMens_RespEsc_PalAval, 2));
    # gini negativo não faz sentido, zera
    vGiniMens_PalAval_RespEsc = vGiniMens_PalAval_RespEsc.clip(min=0)
    if debug: print('gini das mensagens sem cada palavra sendo avaliada e sem a resposta escolhida:')
    if debug: print(vGiniMens_PalAval_RespEsc)

    # calculando o gini de cada palavra
    vGiniPalAval = giniO - ((vGiniMensPalRespEsc * vqMensPalAval / qMens) + \
    (vGiniMens_PalAval_RespEsc * vqMens_PalAval / qMens))
    # gini negativo não faz sentido, zera
    vGiniPalAval = vGiniPalAval.clip(min=0)
    if debug: print('Gini de cada palavra avaliada:')
    if debug: print(vGiniPalAval)

    # melhor palavra: a palavra com o maior GINI
    # TODO ValueError: attempt to get argmax of an empty sequence
    try:
        indPalEsc = np.argmax(vGiniPalAval)
        PalEsc = palavras[indPalEsc +1]
    except ValueError:
        # provisoriamente vamos pegar a primeira palavra disponivel
        PalEsc = [1]
        indPalEsc = 0
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
    # é preciso verificar a invariância das mensagens:
    # comparemos as quantidades de linhas
    if not np.size(mensagens, 0) == np.size(mensagensPalAval, 0) + np.size(mensagens_PalAval, 0):
        print('*'*79)
        print('-'*79)
        print('Erro de invariância no nó ', noDados.retIndice())
        print('pai: ', np.size(mensagens, 0))
        print('esq: ', np.size(mensagensPalAval, 0))
        print('dir: ', np.size(mensagens_PalAval, 0))
        print('*'*79)
        print('-'*79)
        raise  ErroDeInvariancia('Divisão de dados com falha!')
    # ajusta a lista de palavras para os nós filhos (esquerdo e direito)
    palavrasProxNo = np.delete(palavras, [indPalEsc+1])
    if debug: print('palavras proximo no:')
    if debug: print(palavrasProxNo)
    # inicia o calculo dos dados de nós ou folhas
    # à esquerda e a direata que serão retornados.

    # NoDados(indice, palavras, mensagens)
    noDadosEsq = NoDados(indice*2+1, palavrasProxNo, mensagensPalAval)
    noDadosDir = NoDados(indice*2+2, palavrasProxNo, mensagens_PalAval)
    # verifica a expansão da árvore:
    # caso não hajam mais mensagens, ou caso só fique uma resposta,
    # para de expandir
    
    # à esquerda
    
    # primeiro preciso verificar se há menos que duas respostas,
    # melhor agrupar os dados pelas respostas (primeira coluna) 
    # e verificar se há menos de duas linhas, caso sim,
    # é folha!
    # a razão é haver consenso com relação à resposta.

    # segundo preciso verificar o numero de linhas de mensagens,
    # se houver menos que duas mensagens é folha!
    # melhor usar a dimensão 0 (conta linhas)  de matriz para isso.
    # a razão é que não é possível prossseguir dividindo,
    # existe consenso para a resposta.

    # np.unique(), pode resulta em um vetor:
    #  exemplo:
    #  a = [[1 0 0]
    #       [1 0 0]
    #       [2 3 4]]
    #   então,
    #   a[:,0] = [1 1 2]
    #   np.unique(a[:,0]) = [1 2]
    #   np.size(np.unique(a[:,0])) = 2

    # np.unique(mensagensPalAval[:,0] retorna um vetor com
    # os elementos únicos da primeira coluna, as respostas
    noDadosEsqResp = np.unique(mensagensPalAval[:,0])
    # np.size(), resulta em um inteiro:
    # exemplo com matriz:
    # a = [[1 2 3]
    #      [4 5 6]]
    #  então
    #  np.size(a) =  6
    #  np.size(a,0)) =  2 (numero de linhas)
    #  np.size(a,1)) =  3 (numero de colunas)
    # exemplo com vetor:
    # a = [1 2 3]
    #  então
    #  np.size(a) =  3
    #  np.size(a,0)) =  3
    #  np.size(a,1)) = IndexError: tuple index out of range
    if np.size(noDadosEsqResp) < 2 or np.size(mensagensPalAval, 0) <2 \
        or np.size(mensagensPalAval, 1) <2:
        # np.size(noDadosEsqResp) dá o número de respostas.
        #  Se o resultado é menor que 2, indica uma ou
        #  nenhuma resposta: é folha!
        #
        # np.size(mensagensPalAval, 0) dá o número
        #  de linhas: se for <2, não existem mais mensagens,
        #  ou existe apenas uma mensagem: é um nó folha!
        #
        # np.size(mensagensPalAval, 1) dá o número de colunas
        #  na matriz. a primeira coluna é a de respostas, logo
        #  o numero de palavras é o número de colunas -1.
        #  portanto, numero de colunas <2 significa
        #  que não restam mais palavras a processar:
        #  é uma folha!
        noDadosEsq.atribFolha(True)
        # colocamos as respostas na folha (e somente nelas)
        # vão ser sempre vetores, no caso ideal, com apenas
        # um valor.
        if np.size(noDadosEsqResp) > 0:
            noDadosEsq.insRespostas(noDadosEsqResp)
            if debug: print('folha com resposta(s): ', noDadosEsqResp, \
            ' a esquerda do no ', indice)
        else:
            # o ideal é quando a folha tem uma resposta,
            # mas, se não tiver:
            # colocamos as respotas do no pai
            noDadosEsq.insRespostas(np.unique(mensagens[:,0]))
            if debug: print('folha com resposta(s) (do pai): ', \
            np.unique(mensagens[:,0]), ' a esquerda do no ', indice)
    # à direita
    # (obs.: as explicações são as mesmas dadas acima
    # para o processamento de expansão à esquerda).
    noDadosDirResp = np.unique(mensagens_PalAval[:,0])
    if np.size(noDadosDirResp) < 2 or np.size(mensagens_PalAval, 0) <2 \
        or np.size(mensagens_PalAval, 1) <2:
        noDadosDir.atribFolha(True)
        if np.size(noDadosDirResp) >0:
            noDadosDir.insRespostas(noDadosDirResp)
            if debug: print('folha com resposta(s): ', \
            noDadosDirResp, ' a direita do no ', indice)
        else:
            noDadosDir.insRespostas(np.unique(mensagens[:,0]))
            if debug: print('folha com resposta(s) (do pai): ', \
            np.unique(mensagens[:,0]), ' a direita do no ', indice)
    return (noDadosEsq, noDadosDir)

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

    # caminho para persistir a arvore
    caminhoDePersistencia = '../../arvorespklarmazenadas/grupo'
    caminhoDePersistencia += datetime.now().strftime('%Y_%m_%d_%H_%M_%S_%f')[:-4] + '/'
    # caso não exista, cria
    pathlib.Path(caminhoDePersistencia).mkdir(parents=True, exist_ok=True)

    # a arvore é um dicionário
    arvore = {}
    # caso seja nescessário persistir
    #parcialmente a arvore para liberar memória
    arvoresPers = []
    numNosPersistidos = 0
    # uma lista de nós a serem processados
    filaDeNos = []
    filaDeNosProcessados = []
    # o primeiro noDados é pré processado,
    # por exemplo, recebe indice 0 (raiz).
    # os próximos são gerados no calculo do noDados,
    # o indice é calculado usando a formula
    # indice esquerda = 2* indice atual + 1
    # indice direita = 2* indice atual + 2

    # conjunto de treino
    mensagens = []

    
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
        # muito importante
        mensagens = mensagens.astype(float)
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

    totMensO = len(mensagens)
    print('mensagens: ', len(mensagens))
    print('palavras: ', len(palavras))

    print('mensagens:')
    print(mensagens)
    s = (mensagens[:,1:]==1).sum(axis=0, dtype=float)
    print('soma: (a partir da segunda coluna, valores = 1)')
    print(s[:20])
    
    ultimapass = timer()

    # dados do nó raiz
    #noDados = NoDados(indice, palavras, mensagens)
    noDados = NoDados(0, palavras, mensagens)
    filaDeNos.append(noDados)
    numNos = 0
    numFolhas = 0
    numMensFolhas = 0
    while True:
        if paralelizar:
            # vamos tentar usar uma pool para
            # processamento paralelo dos dados dos nós.
            pool = ThreadPool(4)
            # pelas limitaçoes da máquina,
            # quero processar no máximo numMaxNosPar  dados de nós de cada vez
            maxProcessos = min(numMaxNosPar, len(filaDeNos))
            filaDeNosParalelos = []
            for i in range(maxProcessos):
                filaDeNosParalelos.append(filaDeNos.pop(0))
            filaDeNosProcessados = pool.map(calculaNo, filaDeNosParalelos)
            pool.close()
            pool.join()
            if debug: print('Resultado do pool: ',  len(filaDeNosProcessados))
            # vamos processar as filas
            ## colocar o(s) nó(s) calculado(s) na árvore
            for i in range(len(filaDeNosParalelos)):
                noDados = filaDeNosParalelos.pop(0)
                arvore[noDados.retIndice()] = No(noDados)
                numNos += 1
                if debug: print('arvore recebe palavra: ', noDados.retPalavra())
            # os dados de nós retornados que não forem folhas
            # devem ser acrescentados à fila de dados de nós,
            # caso contrário vão para a árvore
            for i in range(len(filaDeNosProcessados)):
                (noDadosEsq, noDadosDir) = filaDeNosProcessados.pop(0)
                noDados = noDadosEsq
                if noDados.eFolha():
                    arvore[noDados.retIndice()] = No(noDados)
                    numFolhas += 1
                    if debug: print('arvore recebe folha')
                else:
                    filaDeNos.append(noDados)
                noDados = noDadosDir
                if noDados.eFolha():
                    arvore[noDados.retIndice()] = No(noDados)
                    numFolhas += 1
                    if debug: print('arvore recebe folha')
                else:
                    filaDeNos.append(noDados)
        else: # não parelelizar
            noDados = filaDeNos.pop(0)
            (noDadosEsq, noDadosDir) = calculaNo(noDados)
            # podemos mais uma vez verificar a invariancia
            # dos dados
            assert np.size(noDados.retMensagens(), 0) == \
            np.size(noDadosEsq.retMensagens(), 0) + np.size(noDadosDir.retMensagens(), 0)
            # coloca o nó processado na árvore
            arvore[noDados.retIndice()] = No(noDados)
            # na verdade, pode ser um nó ou folha!
            if noDados.eFolha():
                numFolhas +=1
                numMensFolhas += np.size(noDados.retMensagens(), 0)
            else:
                numNos += 1
                # se é nó, processa filhos
                noDados = noDadosEsq
                if noDados.eFolha():
                    arvore[noDados.retIndice()] = No(noDados)
                    numFolhas += 1
                    numMensFolhas += np.size(noDados.retMensagens(), 0)
                    if debug: print('arvore recebe folha')
                else:
                    filaDeNos.append(noDados)
                noDados = noDadosDir
                if noDados.eFolha():
                    arvore[noDados.retIndice()] = No(noDados)
                    numFolhas += 1
                    numMensFolhas += np.size(noDados.retMensagens(), 0)
                    if debug: print('arvore recebe folha')
                else:
                    filaDeNos.append(noDados)
            if not len(arvore) == numNos+numFolhas:
                print('largura da arvore: ', len(arvore))
                print('numero de nós: ', numNos)
                print('numero de folhas: ', numFolhas)
                raise ErroDeInvariancia('tamanho da arvore incompatível!')
                #TODO programa interrompido aquí, 26/Nov/2018
        # totalização da rodada
        if (timer() - ultimapass) >= intervaloMostra:
            usoMemoria = py.memory_info()[0]/2.**30  # memory use in GB...I think
            fim = timer()
            print('-'*79)
            print('uso de memoria(GB):', usoMemoria)
            print('Tempo ate agora: ', str(timedelta(seconds=fim - inicio)))
            print('total de nós : ', numNos)
            print('total de folhas: ', numFolhas, ' consumiram ', numMensFolhas, 'mensagens')
            print('mensagens a consumir: ', totMensO, ' mensagens', 'invariancia: ', totMensO - numMensFolhas)
            print('total na arvore : ', numNos + numFolhas)
            print('nos na fila: ', len(filaDeNos))
            print('maior numero de linhas em um no na rodada: ', qmaxmens)
            print('-'*79)
            ultimapass = timer()
            qmaxmens = 0
        if debug: print('Ao fim da repeticao temos para processar: ', len(filaDeNos))
        # se a fila de dados de nos estiver vazia encerra
        if len(filaDeNos)==0:
            usoMemoria = py.memory_info()[0]/2.**30  # memory use in GB...I think
            fim = timer()
            print('='*79)
            print('Processamento encerrado!')
            print('uso de memoria(GB):', usoMemoria)
            print('total de nós : ', numNos)
            print('total de folhas: ', numFolhas)
            print('total na árvore: ', numNos + numFolhas)
            print('total de mensagens em O: ', totMensO)
            print('Tempo de processamento: ', str(timedelta(seconds=fim - inicio)))
            print('='*79)
            break
        # se a arvore estiver muito grande,
        # persiste parcialmente
        # e junta apenas ao final
        if len(arvore) > limitePersArv:
            if debug: print('persistindo parcialmente a arvore.')
            arvoresPers.append(salvarArvore(arvore))
            numNosPersistidos += len(arvore)
            arvore = {}

    # caso a árvore tenha sido persistida em partes
    # no momento, vamos deixar sem essa função ...
    #if len(arvoresPers)>0:
    #    print('reunindo arvore parcialmente persistida.')
    #    for arq in arvoresPers:
    #        arvcp = arvore.copy()
    #        arvrec = CarregarArvore(arq)
    #        arvore = {**arvcp, **arvrec}
    #    fim = timer()
    #    print('Tempo para reunir a arvore: ', str(timedelta(seconds=fim - inicio)))
        
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
        #nomeArq = salvarArvore(arvore)
        #print('arvore salva no arquivo: ', nomeArq)
        # ler arvore
        #arvore = CarregarArvore(nomeArq)
        #print('Percorrendo a arvore recuperada')
        #visitas = 0
        #proximo = [0]
        #while(len(proximo)>0):
        #    ind = proximo.pop(0)
        #    no = arvore.get(ind)
        #    print('no: ', ind)
        #    if not no.eFolha():
        #        proximo.append(ind*2+1)
        #        proximo.append(ind*2+2)
        #        print('  palavra  : ', no.Palavra())
        #    else:
        #        print('  respostas: ', no.Respostas())

    salvarArvore(arvore)
    fim = timer()
    print('#'*79)
    print('Tempo de processamento: ', str(timedelta(seconds=fim - inicio)))
    print('#'*79)

if __name__ == "__main__":
    main()


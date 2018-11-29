#!/bin/python

#modulos

import qasmod
import numpy as np
import os
import csv
from timeit import default_timer as timer
import psutil
import pickle
import itertools
from datetime import datetime
from datetime import timedelta
from multiprocessing.dummy import Pool as ThreadPool
import pathlib

#globais

# se verdadeiro o programa escreve
# várias mensagens. Deve ser usado
# apenas para testes
debug = False
# utiliza dados randômicos
# ao invés de reais.
executarTeste = True
# define as dimensões da
# matriz de teste
tamTeste = [500,60]
# se verdadeiro o programa embaralha
# e divide o arquivo de dados em
# treino (90%) e teste(10%),
# caso contrário usa todos os dados
# tanto para treino como para teste.
# normalmente isso causa overfiting.
particionar = True
# se verdadeiro a expansão da árvore
# é paralelizada
paralelizar = False
# máximo de nós a paralelizar
# a cada pool
numMaxnosPar = 1000

# inicialização dos processos do programa

inicio = timer()
pid = os.getpid()
py = psutil.Process(pid)
# para acompanhar o maior número de mensagens
# processadas em uma rodada de expansão da árvore.
qmaxmens = 0
# para acompanhar quantas mensagens
# já foram processadas
qtotmenscalc = 0
# caso a árvore fique muito grande,
# pode ser parcialmente persistida,
# liberando memória para rodar o programa.
limitePersArv = 100000
# pasta para salvar as árvores obtidas,
# o ideal é ficar pelo menos um nível
# de pasta anterior ao git.
caminhoDePersistencia = '.'
# de quanto em quanto tempo
# o progresso do processamento
# é relatado.
# valor recomendado 5.0
intervaloMostra = 30.0



# métodos auxiliares

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

def calculano(nodados):
    global inicio
    global debug
    global py
    global qmaxmens
    global qtotmenscalc

    indice = nodados.retindice
    palavras = nodados.retpalavras
    mensagens = nodados.retmensagens

    fim = timer()
    qmens = np.shape(mensagens)[0]
    if qmens > qmaxmens:
        qmaxmens = qmens

    if debug:
        print('-'*79)
        usoMemoria = py.memory_info()[0]/2.**30  # memory use in GB...I think
        print('uso de memoria:', usoMemoria)
        print('')
        print('Ate o no ', indice, ': ')
        print(' tempo (em segundos): ', str(timedelta(seconds=fim - inicio)))
        print('quantidade de mensagens: ', qmens)
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
    qmensRespEsc = np.shape(respEscMensagens)[0]
    if debug: print('quantidade de mensagens com a resposta escolhida: ', qmensRespEsc)
    # taxa de mensagens com a resposta escolhida (C)
    tMensRespEsc = dividir(qmensRespEsc, qmens);
    if debug: print('taxa de mensagens com a resposta escolhida: ', tMensRespEsc);
    # taxa de mensagens sem a resposta escolhida (A)
    tMens_RespEsc = dividir((qmens - qmensRespEsc), qmens);
    if debug: print('taxa de mensagens sem a resposta escolhida: ', tMens_RespEsc);
    giniO = 1 - (pow(tMensRespEsc, 2) + pow(tMens_RespEsc, 2));
    # gini negativo não faz sentido ...
    giniO = max(0, giniO);
    if debug: print('GINI de O: ', giniO);
    # calculando o gini de cada palavra
    #  mensagens com cada palavra avaliada e qualquer resposta
    vqmensPalAval = (mensagens[:,1:]==1.0).sum(axis=0, dtype=float)
    if debug: print('mensagens com cada palavra avaliada e qualquer resposta:')
    if debug: print(vqmensPalAval)
    # quantidade de mensagens com a resposta escolhida com cada palavra
    vqmensRespEscPalAval = (respEscMensagens[:,1:]==1.0).sum(axis=0, dtype=float)
    if debug: print('mensagens com cada palavra e a resposta escolhida:')
    if debug: print(vqmensRespEscPalAval)
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
    vtqmensRespEscPalAval = \
    np.divide(vqmensRespEscPalAval, vqmensPalAval, out=np.zeros_like(vqmensRespEscPalAval), \
    where=vqmensPalAval!=0.0, casting='unsafe')
    if debug: print('taxa de mensagens com cada palavra e a resposta escolhida:')
    if debug: print(vtqmensRespEscPalAval)
    # taxa de mensagens com a palavra sendo analisada e a resposta diferente da escolhida
    vqmens_RespEscPalAval = vqmensPalAval - vqmensRespEscPalAval
    vtqmens_RespEscPalAval = \
    np.divide(vqmens_RespEscPalAval, vqmensPalAval, out=np.zeros_like(vqmens_RespEscPalAval), \
    where=vqmensPalAval!=0.0, casting='unsafe')
    if debug: print('taxa de mensagens com cada palavra e resposta diferente da escolhida:')
    if debug: print(vtqmens_RespEscPalAval)
    # gini das mensagens com cada palavra e com a resposta escolhida
    vGiniMensPalRespEsc = 1 - (pow(vtqmensRespEscPalAval, 2) + pow(vtqmens_RespEscPalAval, 2));
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
    vqmens_PalAval = (mensagens[:,1:]==0).sum(axis=0, dtype=float)
    # quantidade de mensagens com a resposta escolhida sem cada palavra
    vqmensRespEsc_PalAval = (respEscMensagens[:,1:]==0).sum(axis=0, dtype=float)
    if debug: print('mensagens com a resposta escolhida e sem cada palavra:')
    if debug: print(vqmensRespEsc_PalAval)
    # taxa de mensagens sem a palavra sendo analisada e com resposta escolhida
    vtqmensRespEsc_PalAval = np.divide(vqmensRespEsc_PalAval, vqmens_PalAval, \
     out=np.zeros_like(vqmensRespEsc_PalAval), where=vqmens_PalAval!=0, casting='unsafe')
    if debug: print('taxa de mensagens com a resposta escolhida e sem cada palavra:')
    if debug: print(vtqmensRespEsc_PalAval)
    # taxa de mensagens sem cada palavra sendo avaliada e resposta diferente da escolhida
    vqmens_RespEsc_PalAval = vqmens_PalAval - vqmensRespEsc_PalAval
    vtqmens_RespEsc_PalAval = np.divide(vqmens_RespEsc_PalAval, vqmens_PalAval, \
     out=np.zeros_like(vqmens_RespEsc_PalAval), where=vqmens_PalAval!=0, casting='unsafe')
    if debug: print('taxa de mensagens sem cada palavra sendo avaliada e resposta diferente da escolhida:')
    if debug: print(vtqmens_RespEsc_PalAval)
    # gini das mensagens sem cada palavra sendo avaliada e sem a resposta escolhida
    vGiniMens_PalAval_RespEsc = 1 - (pow(vtqmensRespEsc_PalAval, 2) + pow(vtqmens_RespEsc_PalAval, 2));
    # gini negativo não faz sentido, zera
    vGiniMens_PalAval_RespEsc = vGiniMens_PalAval_RespEsc.clip(min=0)
    if debug: print('gini das mensagens sem cada palavra sendo avaliada e sem a resposta escolhida:')
    if debug: print(vGiniMens_PalAval_RespEsc)

    # calculando o gini de cada palavra
    vGiniPalAval = giniO - ((vGiniMensPalRespEsc * vqmensPalAval / qmens) + \
    (vGiniMens_PalAval_RespEsc * vqmens_PalAval / qmens))
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
    nodados.inspalavra(PalEsc)
    if debug: print('Melhor palavra: ', PalEsc, ' indice: ', indPalEsc +1)
    if debug: print('conferindo palavra do no: ', nodados.retpalavra)
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
        print('Erro de invariância no nó ', nodados.retindice)
        print('pai: ', np.size(mensagens, 0))
        print('esq: ', np.size(mensagensPalAval, 0))
        print('dir: ', np.size(mensagens_PalAval, 0))
        print('*'*79)
        print('-'*79)
        raise  Exception('Divisão de dados com falha!')
    # ajusta a lista de palavras para os nós filhos (esquerdo e direito)
    palavrasProxno = np.delete(palavras, [indPalEsc+1])
    if debug: print('palavras proximo no:')
    if debug: print(palavrasProxno)
    # inicia o calculo dos dados de nós ou folhas
    # à esquerda e a direata que serão retornados.

    # nodados(indice, palavras, mensagens)
    nodadosEsq = qasmod.nodados(indice*2+1, palavrasProxno, mensagensPalAval)
    nodadosDir = qasmod.nodados(indice*2+2, palavrasProxno, mensagens_PalAval)
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
    nodadosEsqResp = np.unique(mensagensPalAval[:,0])
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
    if np.size(nodadosEsqResp) < 2 or np.size(mensagensPalAval, 0) <2 \
        or np.size(mensagensPalAval, 1) <2:
        # np.size(nodadosEsqResp) dá o número de respostas.
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
        nodadosEsq.atribfolha(True)
        # colocamos as respostas na folha (e somente nelas)
        # vão ser sempre vetores, no caso ideal, com apenas
        # um valor.
        if np.size(nodadosEsqResp) > 0:
            nodadosEsq.insrespostas(nodadosEsqResp)
            if debug: print('folha com resposta(s): ', nodadosEsqResp, \
            ' a esquerda do no ', indice)
        else:
            # o ideal é quando a folha tem uma resposta,
            # mas, se não tiver:
            # colocamos as respotas do no pai
            nodadosEsq.insrespostas(np.unique(mensagens[:,0]))
            if debug: print('folha com resposta(s) (do pai): ', \
            np.unique(mensagens[:,0]), ' a esquerda do no ', indice)
    # à direita
    # (obs.: as explicações são as mesmas dadas acima
    # para o processamento de expansão à esquerda).
    nodadosDirResp = np.unique(mensagens_PalAval[:,0])
    if np.size(nodadosDirResp) < 2 or np.size(mensagens_PalAval, 0) <2 \
        or np.size(mensagens_PalAval, 1) <2:
        nodadosDir.atribfolha(True)
        if np.size(nodadosDirResp) >0:
            nodadosDir.insrespostas(nodadosDirResp)
            if debug: print('folha com resposta(s): ', \
            nodadosDirResp, ' a direita do no ', indice)
        else:
            nodadosDir.insrespostas(np.unique(mensagens[:,0]))
            if debug: print('folha com resposta(s) (do pai): ', \
            np.unique(mensagens[:,0]), ' a direita do no ', indice)
    return (nodadosEsq, nodadosDir)

# método principal

def main():
    
    # globais

    global executarTeste
    global debug
    global inicio
    global py
    global qmaxmens
    global limitePersArv
    global caminhoDePersistencia
    global intervaloMostra
    global numMaxnosPar
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
    numnosPersistidos = 0
    # uma lista de nós a serem processados
    filaDenos = []
    filaDenosProcessados = []
    # o primeiro nodados é pré processado,
    # por exemplo, recebe indice 0 (raiz).
    # os próximos são gerados no calculo do nodados,
    # o indice é calculado usando a formula
    # indice esquerda = 2* indice atual + 1
    # indice direita = 2* indice atual + 2

    # conjunto de mensagens
    mensagens = []
    # conjunto de treino
    treinos = []
    # conjunto de testes
    testes = []
    
    if executarTeste:
        # será gerado um conjunto de dados alatório
        # que serve apenas para testar o código.
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
            palavras = next(reader, none)
            for mensagem in reader:
                mensagens.append(mensagem)
        mensagens = np.asarray(mensagens, dtype = np.dtype('uint32'))
        print('Arquivo csv:')

    if particionar:
        # para particionar matriz
        # treinos = 90%
        # testes = 10%
        np.random.shuffle(mensagens)
        l = mensagens.shape[0]
        treinos, testes = mensagens[: int(l * .9)], mensagens[int(l * .9) :]
        print('>'*79)
        print('Mensagens (', mensagens.shape, ') particionadas.')
        print(' treinos(', treinos.shape, ') e testes(', testes.shape, ')')
        print('>'*79)
        # neste caso é recomendável salvar o treino para posterior execução
    else:
        # se não, usa os mesmos dados
        # para treino e teste
        # aceitando overfiting
        treinos = testes = mensagens

    totMensO = len(treinos)
    print('mensagens: ', len(treinos))
    print('palavras: ', len(palavras))

    print('mensagens:')
    print(treinos)
    s = (treinos[:,1:]==1).sum(axis=0, dtype=float)
    print('soma: (a partir da segunda coluna, valores = 1)')
    print(s[:20])

    ultimapass = timer()

    # dados do nó raiz
    #nodados = nodados(indice, palavras, treinos)
    nodados = qasmod.nodados(0, palavras, treinos)
    filaDenos.append(nodados)
    numnos = 0
    numfolhas = 0
    numMensfolhas = 0
    while True:
        if paralelizar:
            # vamos tentar usar uma pool para
            # processamento paralelo dos dados dos nós.
            pool = ThreadPool(4)
            # pelas limitaçoes da máquina,
            # quero processar no máximo numMaxnosPar  dados de nós de cada vez
            maxProcessos = min(numMaxnosPar, len(filaDenos))
            filaDenosParalelos = []
            for i in range(maxProcessos):
                filaDenosParalelos.append(filaDenos.pop(0))
            filaDenosProcessados = pool.map(calculano, filaDenosParalelos)
            pool.close()
            pool.join()
            if debug: print('Resultado do pool: ',  len(filaDenosProcessados))
            # vamos processar as filas
            ## colocar o(s) nó(s) calculado(s) na árvore
            for i in range(len(filaDenosParalelos)):
                nodados = filaDenosParalelos.pop(0)
                arvore[nodados.retindice] = qasmod.no(nodados)
                numnos += 1
                if debug: print('arvore recebe palavra: ', nodados.retpalavra)
            # os dados de nós retornados que não forem folhas
            # devem ser acrescentados à fila de dados de nós,
            # caso contrário vão para a árvore
            for i in range(len(filaDenosProcessados)):
                (nodadosEsq, nodadosDir) = filaDenosProcessados.pop(0)
                nodados = nodadosEsq
                if nodados.efolha:
                    arvore[nodados.retindice] = qasmod.no(nodados)
                    numfolhas += 1
                    if debug: print('arvore recebe folha')
                else:
                    filaDenos.append(nodados)
                nodados = nodadosDir
                if nodados.efolha:
                    arvore[nodados.retindice] = qasmod.no(nodados)
                    numfolhas += 1
                    if debug: print('arvore recebe folha')
                else:
                    filaDenos.append(nodados)
        else: # não parelelizar
            nodados = filaDenos.pop(0)
            (nodadosEsq, nodadosDir) = calculano(nodados)
            # podemos mais uma vez verificar a invariancia
            # dos dados
            assert np.size(nodados.retmensagens, 0) == \
            np.size(nodadosEsq.retmensagens, 0) + np.size(nodadosDir.retmensagens, 0)
            # coloca o nó processado na árvore
            arvore[nodados.retindice] = qasmod.no(nodados)
            # na verdade, pode ser um nó ou folha!
            if nodados.efolha:
                numfolhas +=1
                numMensfolhas += np.size(nodados.retmensagens, 0)
            else:
                numnos += 1
                # se é nó, processa filhos
                nodados = nodadosEsq
                if nodados.efolha:
                    arvore[nodados.retindice] = qasmod.no(nodados)
                    numfolhas += 1
                    numMensfolhas += np.size(nodados.retmensagens, 0)
                    if debug: print('arvore recebe folha')
                else:
                    filaDenos.append(nodados)
                nodados = nodadosDir
                if nodados.efolha:
                    arvore[nodados.retindice] = qasmod.no(nodados)
                    numfolhas += 1
                    numMensfolhas += np.size(nodados.retmensagens, 0)
                    if debug: print('arvore recebe folha')
                else:
                    filaDenos.append(nodados)
            if not len(arvore) == numnos+numfolhas:
                print('largura da arvore: ', len(arvore))
                print('numero de nós: ', numnos)
                print('numero de folhas: ', numfolhas)
                raise Exception('tamanho da arvore incompatível!')
                #TODO programa interrompido aquí, 26/nov/2018
        # totalização da rodada
        if (timer() - ultimapass) >= intervaloMostra:
            usoMemoria = py.memory_info()[0]/2.**30  # memory use in GB...I think
            fim = timer()
            print('-'*79)
            print('uso de memoria(GB):', usoMemoria)
            print('Tempo ate agora: ', str(timedelta(seconds=fim - inicio)))
            print('total de nós : ', numnos)
            print('total de folhas: ', numfolhas, ' consumiram ', numMensfolhas, 'mensagens')
            print('mensagens a consumir: ', totMensO, ' mensagens', 'invariancia: ', totMensO - numMensfolhas)
            print('total na arvore : ', numnos + numfolhas)
            print('nos na fila: ', len(filaDenos))
            print('maior numero de linhas em um no na rodada: ', qmaxmens)
            print('-'*79)
            ultimapass = timer()
            qmaxmens = 0
        if debug: print('Ao fim da repeticao temos para processar: ', len(filaDenos))
        # se a fila de dados de nos estiver vazia encerra
        if len(filaDenos)==0:
            usoMemoria = py.memory_info()[0]/2.**30  # memory use in GB...I think
            fim = timer()
            print('='*79)
            print('Processamento encerrado!')
            print('uso de memoria(GB):', usoMemoria)
            print('total de nós : ', numnos)
            print('total de folhas: ', numfolhas)
            print('total na árvore: ', numnos + numfolhas)
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
            numnosPersistidos += len(arvore)
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
        
    # salvar a arvore
    salvarArvore(arvore)
    # ler arvore
    #arvore = CarregarArvore(caminhoDePersistencia)
    print('arvore carregada, tamanho: ', len(arvore))
    acertos = 0
    erros = 0
    testadas = 0
    # quantidade de mensagens a testar
    qmensteste = np.size(testes, 0)
    print('mensagens no conjunto de mensagens: ', qmensteste)
    for i in range(qmensteste):
        mensagem = testes[i]
        #pesquisar a arvore gerada iniciando pela raiz
        proximo = [0]
        while(len(proximo)>0):
            ind = proximo.pop(0)
            no = arvore.get(ind)
            if debug: print('no: ', ind)
            if not no.efolha:
                # verifica se a mensagem tem a
                # palavra da arvore ou não.
                palno = no.retpalavra
                if mensagem[palavras.index(palno)] == 1:
                    # mensagem tem a palavra
                    # vai para a esquerda
                    proximo.append(ind*2+1)
                else:
                    # mensagem não tem a palavra
                    # vai para a direita
                    proximo.append(ind*2+2)
            else:
                # hora da decisão
                if mensagem[0] == no.retrespostas[0]:
                    acertos +=1
                else:
                    erros += 1
                testadas += 1
                if debug: print('testadas: ', testadas, ' acertos: ', acertos, ' erros:', erros)
                if debug: print('acuidade: ', acertos*100/testadas)
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
    print('testadas: ', testadas, ' acertos: ', acertos, ' erros:', erros)
    print('acuidade: ', acertos*100/testadas)
    print('Tempo de processamento: ', str(timedelta(seconds=fim - inicio)))
    print('#'*79)

if __name__ == "__main__":
    main()


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

# método principal

def main():
    
    # se verdadeiro o programa escreve
    # várias mensagens. Deve ser usado
    # apenas para testes
    debug = False

    # utiliza dados randômicos
    # ao invés de reais.
    # caso contrário, busca o
    # arquivo Training.csv
    # na subpasta dados.
    executarTeste = False

    # define as dimensões da
    # matriz de teste
    tamTeste = [8,4]

    # se verdadeiro o programa embaralha
    # e divide o arquivo de dados em
    # treino (90%) e teste(10%),
    # caso contrário usa todos os dados
    # tanto para treino como para teste.
    # é de se esperar overfitting.
    particionar = True

    # se verdadeiro a expansão da árvore
    # é paralelizada
    paralelizar = False

    # máximo de nós a paralelizar
    # a cada pool
    num_max_nos_par = 1000

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
    caminho = '.'
    # de quanto em quanto tempo
    # o progresso do processamento
    # é relatado.
    # valor recomendado 5.0
    intervaloMostra = 5.0


    # caminho para persistir a arvore
    caminho = 'dados/arvores/'
    # caso não exista, cria
    pathlib.Path(caminho).mkdir(parents=True, exist_ok=True)

    # a arvore é um dicionário
    arvore = {}
    # caso seja nescessário persistir
    #parcialmente a arvore para liberar memória
    arvoresPers = []
    num_nos_contabPersistidos = 0
    # uma lista de nós a serem processados
    fila_de_nos_dados = []
    fila_de_nos_dados_processados = []
    # o primeiro no_dados_ob é pré processado,
    # por exemplo, recebe indice 0 (raiz).
    # os próximos são gerados no calculo do no_dados_ob,
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
        mensagens[:,0] = np.random.randint(50, 50+tamTeste[0]/2, size=tamTeste[0])
        palavras=['resposta']
        for i in range(np.size(mensagens, 1) -1):
            palavras.append('pal' + str(i+1))
        # muito importante
        mensagens = mensagens.astype(float)
        print('Teste aleatório:')
    else:
        #ler o arquivo csv
        with open("dados/Training.csv", encoding='iso-8859-1') as csvfile:
            reader = csv.reader(csvfile)
            palavras = next(reader, None)
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

    total_de_mensagens_no_sistema = len(treinos)
    print('mensagens: ', len(treinos))
    print('palavras: ', len(palavras))

    print('mensagens:')
    print(treinos)
    s = (treinos[:,1:]==1).sum(axis=0, dtype=float)
    print('soma: (a partir da segunda coluna, valores = 1)')
    print(s[:20])

    ultimapass = timer()

    # dados do nó raiz
    #no_dados_ob = no_dados_ob(indice, palavras, treinos)
    no_dados_ob = qasmod.nodados(0, palavras, treinos)
    fila_de_nos_dados.append(no_dados_ob)
    num_nos_contab = 0
    num_folhas_contab = 0
    num_mens_folhas_contab = 0
    max_div_mens_contab = 0
    while True:
        if paralelizar:
            # vamos tentar usar uma pool para
            # processamento paralelo dos dados dos nós.
            pool = ThreadPool(4)
            # pelas limitaçoes da máquina,
            # quero processar no máximo num_max_nos_par  dados de nós de cada vez
            max_processos = min(num_max_nos_par, len(fila_de_nos_dados))
            fila_de_nos_dados_paralelos = []
            for i in range(max_processos):
                fila_de_nos_dados_paralelos.append(fila_de_nos_dados.pop(0))
            fila_de_nos_dados_processados = pool.map(qasmod.calcula_no, fila_de_nos_dados_paralelos)
            pool.close()
            pool.join()
            if debug: print('Resultado do pool: ',  len(fila_de_nos_dados_processados))
            # vamos processar as filas
            ## colocar o(s) nó(s) calculado(s) na árvore
            # os dados de nós retornados que não forem folhas
            # devem ser acrescentados à fila de dados de nós,
            # caso contrário vão para a árvore
            for i in range(len(fila_de_nos_dados_processados)):
                # processa o par de dados retornado pelo calculo
                (no_dados_ob_esq, no_dados_ob_dir) = fila_de_nos_dados_processados.pop(0)
                no_dados_ob = no_dados_ob_esq
                if no_dados_ob.efolha:
                    arvore[no_dados_ob.retindice] = qasmod.no(no_dados_ob)
                    num_folhas_contab += 1
                    if debug: print('arvore recebe folha')
                else:
                    fila_de_nos_dados.append(no_dados_ob)
                no_dados_ob = no_dados_ob_dir
                if no_dados_ob.efolha:
                    arvore[no_dados_ob.retindice] = qasmod.no(no_dados_ob)
                    num_folhas_contab += 1
                    if debug: print('arvore recebe folha')
                else:
                    fila_de_nos_dados.append(no_dados_ob)
        else: # não parelelizar
            no_dados_ob = fila_de_nos_dados.pop(0)
            (no_dados_ob_esq, no_dados_ob_dir) = qasmod.calcula_no(no_dados_ob, debug)
            # podemos mais uma vez verificar a invariancia
            # dos dados
            assert np.size(no_dados_ob.retmensagens, 0) == \
            np.size(no_dados_ob_esq.retmensagens, 0) + np.size(no_dados_ob_dir.retmensagens, 0)
            # coloca o nó processado na árvore
            arvore[no_dados_ob.retindice] = qasmod.no(no_dados_ob)
            # contabiliza o novo nó da árvore
            num_nos_contab += 1
            # processa filhos
            no_dados_ob = no_dados_ob_esq
            # podemos contabilizar para cada período
            # a divisão máxima de nós observada
            qmo = np.size(no_dados_ob.retmensagens, 0)
            if qmo > max_div_mens_contab:
                max_div_mens_contab = qmo
            if no_dados_ob.efolha:
                arvore[no_dados_ob.retindice] = qasmod.no(no_dados_ob)
                num_folhas_contab += 1
                num_mens_folhas_contab += qmo
                total_de_mensagens_no_sistema -= qmo
                if debug: print('arvore recebe folha')
            else:
                fila_de_nos_dados.append(no_dados_ob)
            no_dados_ob = no_dados_ob_dir
            # podemos contabilizar para cada período
            # a divisão máxima de nós observada
            qmo = np.size(no_dados_ob.retmensagens, 0)
            if qmo > max_div_mens_contab:
                max_div_mens_contab = qmo
            if no_dados_ob.efolha:
                arvore[no_dados_ob.retindice] = qasmod.no(no_dados_ob)
                num_folhas_contab += 1
                num_mens_folhas_contab += qmo
                total_de_mensagens_no_sistema -= qmo
                if debug: print('arvore recebe folha')
            else:
                fila_de_nos_dados.append(no_dados_ob)
            if not len(arvore) == num_nos_contab+num_folhas_contab:
                print('largura da arvore: ', len(arvore))
                print('numero de nós: ', num_nos_contab)
                print('numero de folhas: ', num_folhas_contab)
                raise Exception('tamanho da arvore incompatível!')
                #TODO programa interrompido aquí, 26/nov/2018
        # contabilização da rodada
        if (timer() - ultimapass) >= intervaloMostra:
            usoMemoria = py.memory_info()[0]/2.**30  # memory use in GB...I think
            fim = timer()
            print('-'*79)
            print('uso de memoria(GB):', usoMemoria)
            print('Tempo ate agora: ', str(timedelta(seconds=fim - inicio)))
            print('total de nós : ', num_nos_contab)
            print('total de folhas: ', num_folhas_contab, ' consumiram ', num_mens_folhas_contab, 'mensagens')
            print('total na arvore : ', num_nos_contab + num_folhas_contab)
            print('mensagens a consumir: ', total_de_mensagens_no_sistema)
            print('nos na fila: ', len(fila_de_nos_dados))
            print('maior divisão de mensagens no período: ', max_div_mens_contab)
            max_div_mens_contab = 0
            print('-'*79)
            ultimapass = timer()
        if debug: print('Ao fim da repeticao temos para processar: ', len(fila_de_nos_dados))
        # se a fila de dados de nos estiver vazia encerra
        if len(fila_de_nos_dados)==0:
            usoMemoria = py.memory_info()[0]/2.**30  # memory use in GB...I think
            fim = timer()
            total_de_mensagens_no_sistema = len(treinos)
            print('='*79)
            print('Processamento encerrado!')
            print('uso de memoria(GB):', usoMemoria)
            print('total de nós : ', num_nos_contab)
            print('total de folhas: ', num_folhas_contab)
            print('total na árvore: ', num_nos_contab + num_folhas_contab)
            print('total de mensagens em O: ', total_de_mensagens_no_sistema)
            print('Tempo de processamento: ', str(timedelta(seconds=fim - inicio)))
            print('='*79)
            break
        # se a arvore estiver muito grande,
        # persiste parcialmente
        # e junta apenas ao final
        if len(arvore) > limitePersArv:
            if debug: print('persistindo parcialmente a arvore.')
            arvoresPers.append(qasmod.salvar_arvore(arvore))
            num_nos_contabPersistidos += len(arvore)
            arvore = {}

    # caso a árvore tenha sido persistida em partes
    # no momento, vamos deixar sem essa função ...
    #if len(arvoresPers)>0:
    #    print('reunindo arvore parcialmente persistida.')
    #    for arq in arvoresPers:
    #        arvcp = arvore.copy()
    #        arvrec = qasmod.carregar_arvore(caminho, arq)
    #        arvore = {**arvcp, **arvrec}
    #    fim = timer()
    #    print('Tempo para reunir a arvore: ', str(timedelta(seconds=fim - inicio)))
        
    # salvar a arvore
    qasmod.salvar_arvore(arvore, caminho)
    # ler arvore
    #arvore = qasmod.carregar_arvore(caminho)
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


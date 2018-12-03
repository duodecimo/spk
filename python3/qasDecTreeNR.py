#!/bin/python

# módulos

import csv
import os
import pathlib
from datetime import timedelta
from multiprocessing.dummy import Pool as ThreadPool
from timeit import default_timer as timer
import numpy as np
import psutil
import qasmod


# método principal

def main():

    # se verdadeiro o programa escreve
    # várias mensagens. É recomendado usar
    # apenas para testes
    debug = False

    # utiliza dados randômicos
    # ao invés de reais.
    # caso contrário, busca o
    # arquivo Training.csv
    # na subpasta dados.
    executar_teste = False

    # define as dimensões da
    # matriz de teste
    tam_teste = [200, 20]

    # se verdadeiro o programa embaralha
    # e divide o arquivo de dados em
    # treino(tx_part_treino) e
    # teste(1 - tx_part_treino),
    # caso contrário usa todos os dados
    # tanto para treino como para teste.
    # é de se esperar overfitting.
    particionar = True

    # informa a taxa de particionamento do
    # conjunto de dados em treino e teste,
    # por exemplo, .9 indica 90% para treino
    # e 10% para teste.
    tx_part_treino = .7

    # se vai haver particionamento,
    # após particionar, pode-se inflar
    # os dados de treino somando o conjunto
    # a sí mesmo tx_infla_treino vezes
    # e embaralhado.
    # Deve ser um número inteiro,
    # de 1 a 5.
    tx_infla_treino = 3
    assert type(tx_infla_treino) is int, "tx_infla_treino não é um inteiro: %r" % tx_infla_treino
    assert 0 < tx_infla_treino < 6, "tx_infla_treino não está ente 1 e 5: %r" % tx_infla_treino

    # se verdadeiro a expansão da árvore
    # é paralelizada
    paralelizar = False

    # máximo de nós a paralelizar
    # a cada pool
    num_max_nos_par = 1000

    # método de escolha da melhor palavra
    # existem 3 métodos à disposição:
    # 1: escolher_melhor_palavra_gini_uma_resposta(mensagens, palavras, q_mens, debug)
    # 2: escolher_melhor_palavra_gini_total(mensagens, palavras, q_mens, debug=False)
    # 3: escolher_melhor_palavra_divisao_maxima(mensagens, palavras)
    metodos_mp = ['gini de uma resposta', 'gini total', 'máxima divisão']
    metodo_mp_escolhido = 1

    # inicialização dos processos do programa

    inicio = timer()
    pid = os.getpid()
    py = psutil.Process(pid)
    # caso a árvore fique muito grande,
    # pode ser parcialmente persistida,
    # liberando memória para rodar o programa.
    limite_pers_arv = 100000
    # de quanto em quanto tempo
    # o progresso do processamento
    # é relatado.
    # valor recomendado 5.0
    intervalo_mostra = 5.0

    # caminho para persistir a arvore
    caminho = 'dados/arvores/'
    # caso não exista, cria
    pathlib.Path(caminho).mkdir(parents=True, exist_ok=True)

    # a arvore é um dicionário
    arvore = {}
    # caso seja necessário persistir
    # parcialmente a arvore para liberar memória
    arvores_pers = []
    num_nos_contab_persistidos = 0
    # uma lista de nós a serem processados
    fila_de_nos_dados = []
    fila_de_nos_dados_processados = []
    # o primeiro no_dados_ob é pré processado,
    # por exemplo, recebe indice 0 (raiz).
    # os próximos são gerados No calculo do no_dados_ob,
    # o índice é calculado usando a formula
    # índice esquerda = 2* índice atual + 1
    # índice direita = 2* índice atual + 2

    # conjunto de mensagens
    mensagens = []
    # conjunto de treino
    treinos = []
    # conjunto de testes
    testes = []

    if executar_teste:
        # será gerado um conjunto de dados aleatório
        # que serve apenas para testar o código.
        intervalo_mostra = 0.00005
        # gerar treino randômico, para testes
        # x, y = 40,20
        mensagens = np.random.randint(2, size=(tam_teste[0], tam_teste[1]))
        # primeira linha, palavras
        mensagens[:, 0] = np.random.randint(50, 50 + tam_teste[0] / 2, size=tam_teste[0])
        palavras = ['resposta']
        for i in range(np.size(mensagens, 1) - 1):
            palavras.append('pal' + str(i + 1))
        # muito importante
        mensagens = mensagens.astype(float)
        print('Teste aleatório:')
    else:
        # ler o arquivo csv
        with open("dados/Training.csv", encoding='iso-8859-1') as csvfile:
            reader = csv.reader(csvfile)
            palavras = next(reader, None)
            for mensagem in reader:
                mensagens.append(mensagem)
        mensagens = np.asarray(mensagens, dtype=np.dtype('uint32'))
        print('Arquivo csv:')

    if particionar:
        # para particionar matriz
        # treinos = tx_part_treino
        # testes = 1 - tx_part_treino

        # vamos utilizar seed=0 para
        # garantir a repetitividade
        # dos dados para testes recorrentes.
        np.random.seed(0)
        np.random.shuffle(mensagens)
        l = mensagens.shape[0]
        treinos, testes = mensagens[: int(l * tx_part_treino)], mensagens[int(l * tx_part_treino):]
        # inflar treino
        if tx_infla_treino>1:
            t = treinos
            for i in range(tx_infla_treino):
                treinos = np.append(treinos, t, axis=0)
            np.random.shuffle(mensagens)
        print('>' * 79)
        if tx_infla_treino > 1:
            print('Mensagens (', mensagens.shape, ') particionadas e infladas ', tx_infla_treino, ' vezes.')
        else:
            print('Mensagens (', mensagens.shape, ') particionadas.')
        print(' treinos(', treinos.shape, ') e testes(', testes.shape, ')')
        print('>' * 79)
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
    s = (treinos[:, 1:] == 1).sum(axis=0, dtype=float)
    print('soma: (a partir da segunda coluna, valores = 1)')
    print(s[:20])

    ultimapass = timer()

    # dados do nó raiz
    # no_dados_ob = no_dados_ob(indice, palavras, treinos)
    no_dados_ob = qasmod.NoDados(0, palavras, treinos)
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
            # quero processar No máximo num_max_nos_par  dados de nós de cada vez
            max_processos = min(num_max_nos_par, len(fila_de_nos_dados))
            fila_de_nos_dados_paralelos = []
            for i in range(max_processos):
                fila_de_nos_dados_paralelos.append(fila_de_nos_dados.pop(0))
            fila_de_nos_dados_processados = pool.map(qasmod.calcula_no, fila_de_nos_dados_paralelos)
            pool.close()
            pool.join()
            if debug: print('Resultado do pool: ', len(fila_de_nos_dados_processados))
            # vamos processar as filas
            # colocar o(s) nó(s) calculado(s) na árvore
            # os dados de nós retornados que não forem folhas
            # devem ser acrescentados à fila de dados de nós,
            # caso contrário vão para a árvore
            for i in range(len(fila_de_nos_dados_processados)):
                # processa o par de dados retornado pelo calculo
                (no_dados_ob_esq, no_dados_ob_dir) = fila_de_nos_dados_processados.pop(0)
                no_dados_ob = no_dados_ob_esq
                if no_dados_ob.efolha:
                    arvore[no_dados_ob.retindice] = qasmod.No(no_dados_ob)
                    num_folhas_contab += 1
                    if debug: print('arvore recebe folha')
                else:
                    fila_de_nos_dados.append(no_dados_ob)
                no_dados_ob = no_dados_ob_dir
                if no_dados_ob.efolha:
                    arvore[no_dados_ob.retindice] = qasmod.No(no_dados_ob)
                    num_folhas_contab += 1
                    if debug: print('arvore recebe folha')
                else:
                    fila_de_nos_dados.append(no_dados_ob)
        else:  # não parelelizar
            no_dados_ob = fila_de_nos_dados.pop(0)
            (no_dados_ob_esq, no_dados_ob_dir) = qasmod.calcula_no(no_dados_ob, metodo_mp_escolhido, debug)
            # podemos mais uma vez verificar a invariancia
            # dos dados
            assert np.size(no_dados_ob.retmensagens, 0) == \
                   np.size(no_dados_ob_esq.retmensagens, 0) + np.size(no_dados_ob_dir.retmensagens, 0)
            # coloca o nó processado na árvore
            arvore[no_dados_ob.retindice] = qasmod.No(no_dados_ob)
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
                arvore[no_dados_ob.retindice] = qasmod.No(no_dados_ob)
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
                arvore[no_dados_ob.retindice] = qasmod.No(no_dados_ob)
                num_folhas_contab += 1
                num_mens_folhas_contab += qmo
                total_de_mensagens_no_sistema -= qmo
                if debug: print('arvore recebe folha')
            else:
                fila_de_nos_dados.append(no_dados_ob)
            if not len(arvore) == num_nos_contab + num_folhas_contab:
                print('largura da arvore: ', len(arvore))
                print('numero de nós: ', num_nos_contab)
                print('numero de folhas: ', num_folhas_contab)
                raise Exception('tamanho da arvore incompatível!')
        # contabilização da rodada
        if (timer() - ultimapass) >= intervalo_mostra:
            uso_memoria = py.memory_info()[0] / 2. ** 30  # memory use in GB...I think
            fim = timer()
            print('-' * 79)
            print('uso de memoria(GB):', uso_memoria)
            print('Tempo ate agora: ', str(timedelta(seconds=fim - inicio)))
            print('total de nós : ', num_nos_contab)
            print('total de folhas: ', num_folhas_contab, ' consumiram ', num_mens_folhas_contab, 'mensagens')
            print('total na arvore : ', num_nos_contab + num_folhas_contab)
            print('mensagens a consumir: ', total_de_mensagens_no_sistema)
            print('nos na fila: ', len(fila_de_nos_dados))
            print('maior divisão de mensagens no período: ', max_div_mens_contab)
            max_div_mens_contab = 0
            print('-' * 79)
            ultimapass = timer()
        if debug: print('Ao fim da repeticao temos para processar: ', len(fila_de_nos_dados))
        # se a fila de dados de nos estiver vazia encerra
        if len(fila_de_nos_dados) == 0:
            uso_memoria = py.memory_info()[0] / 2. ** 30  # memory use in GB...I think
            fim = timer()
            total_de_mensagens_no_sistema = len(treinos)
            print('=' * 79)
            print('Processamento encerrado!')
            print('uso de memoria(GB):', uso_memoria)
            print('total de nós : ', num_nos_contab)
            print('total de folhas: ', num_folhas_contab)
            print('total na árvore: ', num_nos_contab + num_folhas_contab)
            print('total de mensagens em O: ', total_de_mensagens_no_sistema)
            print('Tempo de processamento: ', str(timedelta(seconds=fim - inicio)))
            print('=' * 79)
            break
        # se a arvore estiver muito grande,
        # persiste parcialmente
        # e junta apenas ao final
        if len(arvore) > limite_pers_arv:
            if debug: print('persistindo parcialmente a arvore.')
            arvores_pers.append(qasmod.salvar_arvore(arvore, caminho))
            num_nos_contab_persistidos += len(arvore)
            arvore = {}

    # caso a árvore tenha sido persistida em partes
    # No momento, vamos deixar sem essa função ...
    # if len(arvores_pers)>0:
    #    print('reunindo arvore parcialmente persistida.')
    #    for arq in arvores_pers:
    #        arvcp = arvore.copy()
    #        arvrec = qasmod.carregar_arvore(caminho, arq)
    #        arvore = {**arvcp, **arvrec}
    #    fim = timer()
    #    print('Tempo para reunir a arvore: ', str(timedelta(seconds=fim - inicio)))

    # salvar a arvore
    qasmod.salvar_arvore(arvore, caminho)
    # ler arvore
    # arvore = qasmod.carregar_arvore(caminho)
    # print('arvore carregada, tamanho: ', len(arvore))

    # fazer teste com os dados de treino
    testadas, acertos, erros, sem_respostas = qasmod.testar_arvore(arvore, treinos, palavras, debug)

    fim = timer()
    print('#' * 79)
    print('método utilizado para escolher a melhor palavra: ', metodos_mp[metodo_mp_escolhido-1])
    print('utilizando os dados de treinamento (espera-se overfitting)')
    if particionar and tx_infla_treino>1:
        print('observação: os dados de treino, após o particionamento, foram inflados ', tx_infla_treino, ' vezes.')
    print('testadas: ', testadas)
    print(' acertos: ', acertos)
    print(' erros: ', erros)
    print(' sem resposta: ', sem_respostas)
    print('acuidade: ', acertos * 100 / (acertos + erros))
    print('Tempo de processamento: ', str(timedelta(seconds=fim - inicio)))
    print('#' * 79)

    if particionar:
        # fazer teste com os dados de teste
        testadas, acertos, erros, sem_respostas = qasmod.testar_arvore(arvore, testes, palavras, debug)

        fim = timer()
        print('#' * 79)
        print('método utilizado para escolher a melhor palavra: ', metodos_mp[metodo_mp_escolhido-1])
        print('utilizando os dados de teste', tx_part_treino*100, '% dos dados originais separados aleatoriamente')
        print('testadas: ', testadas)
        print(' acertos: ', acertos)
        print(' erros: ', erros)
        print(' sem resposta: ', sem_respostas)
        print('acuidade: ', acertos * 100 / (acertos + erros))
        print('Tempo de processamento: ', str(timedelta(seconds=fim - inicio)))
        print('#' * 79)


if __name__ == "__main__":
    main()

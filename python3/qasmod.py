# modulos

import pathlib
import pickle
from datetime import datetime
from datetime import timedelta
from timeit import default_timer as timer

import numpy as np
import csv


# classes

class NoDados:

    # possui atributos para processar e gerar o No da arvore
    def __init__(self, indice, palavras, mensagens):
        self.__indice = indice  # vai ser o indice do dicionario arvore
        self.__palavra = None  # a melhor palavra que divide os nós
        self.__respostas = None  # lista de respostas
        self.__mensagens = mensagens  # matriz de mensagens a serem processadas
        self.__palavras = palavras  # vetor de palavras a serem processadas
        self.__folha = False  # indica se um nó é ou não folha

    @property
    def retindice(self):
        return self.__indice

    def inspalavra(self, palavra):
        self.__palavra = palavra

    @property
    def retpalavra(self):
        return self.__palavra

    def insrespostas(self, respostas):
        self.__respostas = respostas

    @property
    def retrespostas(self):
        return self.__respostas

    def insmensagens(self, mensagens):
        self.__mensagens = mensagens

    @property
    def retmensagens(self):
        return self.__mensagens

    @property
    def retpalavras(self):
        return self.__palavras

    def atribfolha(self, val):
        self.__folha = val

    @property
    def efolha(self):
        return self.__folha


class No:

    # é o objeto do dicionário árvore
    # recebe como parâmetro um objeto NoDados,
    # de onde extrai todos seus atributos
    def __init__(self, nodados_ob):
        self.__palavra = nodados_ob.retpalavra  # utilizada para dividir a árvore, ausente em folhas
        self.__respostas = nodados_ob.retrespostas
        self.__folha = nodados_ob.efolha

    @property
    def retpalavra(self):
        return self.__palavra

    @property
    def retrespostas(self):
        return self.__respostas

    @property
    def efolha(self):
        return self.__folha


# métodos auxiliares

def dividir(x, y: object):
    if y == 0:
        return 0
    return x / y


def salvar_arvore(arvore, caminho):
    comp = datetime.now().strftime('%Y_%m_%d_%H_%M_%S_%f')[:-2]
    # utiliza a forma arvore_<timestamp>.pkl para o arquivo,
    # garantindo a unicidade do nome em seguidas
    # execuções do programa.
    nome_arq = caminho + 'arvore_' + comp + '.pkl'
    # utiliza apenas arvore.pfl para o arquivo,
    # sempre sobrescrevendo o anterior, garantindo
    # desta forma acesso com um nome garantido
    # à última árvore gerada.
    nome_arq2 = caminho + 'arvore.pkl'
    arq = open(nome_arq, 'wb')
    pickle.dump(arvore, arq, pickle.HIGHEST_PROTOCOL)
    arq.close()
    try:
        pathlib.Path(nome_arq2).unlink()
    except FileNotFoundError:
        pass
    arq = open(nome_arq2, 'wb')
    pickle.dump(arvore, arq, pickle.HIGHEST_PROTOCOL)
    arq.close()

    nome_arq3 = caminho + 'arvore.csv'
    with open(nome_arq3, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile, delimiter=',')
        writer.writerow(['id', 'palavra', 'resposta'])
        for chave, no in arvore.items():
            pl = no.retpalavra
            if pl is None:
                pl = 'null'
            rp = no.retrespostas
            if rp is None or len(rp) == 0:
                rp = 'null'
            else:
                rp = rp[0]
            writer.writerow([chave, pl, rp])

    return nome_arq


def carregar_arvore(arq='arvore.pkl'):
    arqref = open(arq, 'rb')
    arvore = pickle.load(arqref)
    arqref.close()
    return arvore


def dividir_arvore(arvore):
    n = len(arvore) // 2
    i = iter(arvore.items())  # alternatively, i = d.iteritems() works in Python 2

    arvore1 = dict(itertools.islice(i, n))  # grab first n items
    arvore2 = dict(i)  # grab the rest

    return arvore1, arvore2


def calcula_no(nodados_ob, metodo_melhor_palavra=3, debug=False):
    indice = nodados_ob.retindice
    palavras = nodados_ob.retpalavras
    mensagens = nodados_ob.retmensagens

    fim = timer()
    q_mens = np.shape(mensagens)[0]

    # if q_mens > qmaxmens:
    #    qmaxmens = q_mens

    if debug:
        uso_memoria = py.memory_info()[0] / 2. ** 30  # memory use in GB...I think
        print('uso de memoria:', uso_memoria)
        print('')
        print('Ate o No ', indice, ': ')
        print(' tempo (em segundos): ', str(timedelta(seconds=fim - inicio)))
        print('quantidade de mensagens: ', q_mens)
        print('-' * 79)

    # escolher melhor palavra
    if metodo_melhor_palavra == 1:
        [pal_esc, ind_pal_esc] = escolher_melhor_palavra_gini_uma_resposta(mensagens, palavras, debug)
    elif metodo_melhor_palavra == 2:
        [pal_esc, ind_pal_esc] = escolher_melhor_palavra_gini_total(mensagens, palavras, debug=False)
    else:
        [pal_esc, ind_pal_esc] = escolher_melhor_palavra_divisao_maxima(mensagens, palavras)

    # inserir nos dados do nó a palavra que divide a árvore
    nodados_ob.inspalavra(pal_esc)
    if debug: print('Melhor palavra: ', pal_esc, ' índice: ', ind_pal_esc + 1)
    if debug: print('conferindo palavra do objeto NoDados: ', nodados_ob.retpalavra)
    # dividir as mensagens entre as que contém a palavra com melhor GINI e as que não.
    mensagens_com_pal_aval = mensagens[mensagens[:, ind_pal_esc + 1] == 1]
    mensagens_sem_pal_aval = mensagens[mensagens[:, ind_pal_esc + 1] == 0]
    if debug: print('mensagens que contém a melhor palavra: (', np.size(mensagens_com_pal_aval, 0), ' linhas)')
    if debug: print(mensagens_com_pal_aval)
    if debug: print('mensagens sem a melhor palavra: (', np.size(mensagens_sem_pal_aval, 0), ' linhas)')
    if debug: print(mensagens_sem_pal_aval)
    # remove a palavra dos novos conjuntos de mensagens (esquerdo e direito)
    mensagens_com_pal_aval = np.delete(mensagens_com_pal_aval, [ind_pal_esc + 1], axis=1)
    mensagens_sem_pal_aval = np.delete(mensagens_sem_pal_aval, [ind_pal_esc + 1], axis=1)
    # ajusta a lista de palavras para os nós filhos (esquerdo e direito)
    palavras_prox_no = np.delete(palavras, ind_pal_esc + 1)
    if debug: print('palavras para o próximo nó:')
    if debug: print(palavras_prox_no)
    # inicia o calculo dos dados de nós ou folhas
    # à esquerda e a direita que serão retornados.

    # NoDados(indice, palavras, mensagens)
    nodados_ob_esq = NoDados(indice * 2 + 1, palavras_prox_no, mensagens_com_pal_aval)
    nodados_ob_dir = NoDados(indice * 2 + 2, palavras_prox_no, mensagens_sem_pal_aval)
    # verifica a expansão da árvore:
    # caso não hajam mais mensagens ou apenas uma mensagem, e/ou
    # caso só fique uma resposta ou nenhuma, para de expandir e cria folha

    # à esquerda

    # primeiro preciso verificar se há menos que duas respostas,
    # melhor agrupar os dados pelas respostas (primeira coluna) 
    # e verificar se há menos de duas linhas, caso sim,
    # é folha!
    # a razão é haver consenso com relação à resposta (ou ausência de uma).

    # segundo preciso verificar o numero de linhas de mensagens,
    # se houver menos que duas mensagens é folha!
    # melhor usar a dimensão 0 (conta linhas)  de matriz para isso.
    # a razão é que não é possível prosseguir dividindo,
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

    # np.unique(mensagens_com_pal_aval[:,0]) retorna um vetor com
    # os elementos únicos da primeira coluna, as respostas
    nodados_esq_resp, count_nodados_esq_resp = np.unique(mensagens_com_pal_aval[:, 0], return_counts=True)
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
    if np.size(nodados_esq_resp) < 2 or np.size(mensagens_com_pal_aval, 0) < 2 \
            or np.size(mensagens_com_pal_aval, 1) < 2:
        # np.size(nodados_esq_resp) dá o número de respostas.
        #  Se o resultado é menor que 2, indica uma ou
        #  nenhuma resposta: é folha!
        #
        # np.size(mensagens_com_pal_aval, 0) dá o número
        #  de linhas: se for <2, não existem mais mensagens,
        #  ou existe apenas uma mensagem: é um nó folha!
        #
        # np.size(mensagens_com_pal_aval, 1) dá o número de colunas
        #  na matriz. a primeira coluna é a de respostas, logo
        #  o numero de palavras é o número de colunas -1.
        #  portanto, numero de colunas <2 significa
        #  que não restam mais palavras a processar:
        #  é uma folha!
        nodados_ob_esq.atribfolha(True)
        # colocamos as respostas na folha (e somente nelas)
        # vão ser sempre vetores, No caso ideal, com apenas
        # um valor.
        # vamos verificar a presença de mais de uma resposta
        if np.size(nodados_esq_resp) > 1:
            # escolher a resposta que ocorre mais vezes
            nd_respostas, contagem = np.unique(mensagens_com_pal_aval[:, 0], return_counts=True)
            nodados_ob_esq.insrespostas([nodados_esq_resp[np.argmax(count_nodados_esq_resp)]])

            print('x' * 79)
            print('nodados_esq_resp: ')
            print(nodados_esq_resp)
            print('count_nodados_esq_resp')
            print(count_nodados_esq_resp)
            print('resultado')
            print([nodados_esq_resp[np.argmax(count_nodados_esq_resp)]])
            print('x' * 79)

        else:
            nodados_ob_esq.insrespostas(nodados_esq_resp)
        # provisoriamente anular o desvio acima
        # nodados_ob_esq.insrespostas(nodados_esq_resp)
        if debug: print('folha com resposta(s): ', nodados_esq_resp,
                        ' a esquerda do No ', indice)
    # à direita
    # (obs.: as explicações são as mesmas dadas acima
    # para o processamento de expansão à esquerda).
    nodados_dir_resp, count_nodados_dir_resp = np.unique(mensagens_sem_pal_aval[:, 0], return_counts=True)
    if np.size(nodados_dir_resp) < 2 or np.size(mensagens_sem_pal_aval, 0) < 2 \
            or np.size(mensagens_sem_pal_aval, 1) < 2:
        nodados_ob_dir.atribfolha(True)
        # vamos verificar a presença de mais de uma resposta
        if np.size(nodados_dir_resp) > 1:
            # escolher a resposta que ocorre mais vezes
            nodados_ob_dir.insrespostas([nodados_dir_resp[np.argmax(count_nodados_dir_resp)]])

            print('x' * 79)
            print('nodados_dir_resp: ')
            print(nodados_dir_resp)
            print('count_nodados_dir_resp')
            print(count_nodados_dir_resp)
            print('resultado')
            print([nodados_dir_resp[np.argmax(count_nodados_dir_resp)]])
            print('x' * 79)

        else:
            nodados_ob_dir.insrespostas(nodados_dir_resp)
        if debug: print('folha com resposta(s): ',
                        nodados_dir_resp, ' a direita do No ', indice)
    return [nodados_ob_esq, nodados_ob_dir]


def escolher_melhor_palavra_gini_total(mensagens, palavras, debug=False):
    # para o gini do conjunto
    q_mens = np.shape(mensagens)[0]

    # subtotais cada resposta
    _, vet_sub_tot_resps = np.unique(mensagens[:, 0], return_counts=True)
    tot_resps = np.sum(vet_sub_tot_resps)
    sum_probs_resps = np.power(vet_sub_tot_resps.astype(dtype=float) / tot_resps, 2)
    #with np.errstate(divide='raise'):
    #    try:
    #        sum_probs_resps = np.power(np.divide(vet_sub_tot_resps, tot_resps, dtype=float), 2)
    #    except Exception:
    #        print('opa, divisão por zero?????')
    #        print('tot_resps: ', tot_resps)
    #        print('np.size(mensagens[:, 0]): ', np.size(mensagens[:, 0]))
    #        print('len(vet_sub_tot_resps): ', len(vet_sub_tot_resps))
    #        print('vet_sub_tot_resps: ', vet_sub_tot_resps)
    #        quit()
    gini_mensagens = 1 - np.sum(sum_probs_resps)
    # TODO ainda encontrando zero!
    # para cada palavra

    # com resposta
    # subtotais de cada resposta
    unq, unq_inv = np.unique(mensagens[:, 0], return_inverse=True)
    out = np.zeros((len(unq), mensagens.shape[1]), dtype=mensagens.dtype)
    out[:, 0] = unq
    # cada palavra: total de cada resposta = 1
    np.add.at(out[:, 1:], unq_inv, mensagens[:, 1:])
    if debug: print('respostas 1: \n', out)
    # gini cada palavra com resposta: [(total de cada resposta = 1) / (total de respostas)] ** 2
    gini_com_resposta = 1 - np.sum(np.power((out[:, 1:]).astype(dtype=float) / q_mens, 2), axis=0)
    if debug: print('gini com resposta: \n', gini_com_resposta)
    # sem resposta
    # troca zeros por um e vice versa nos valores, att: danifica a coluna de respostas
    msr = np.logical_not(mensagens).astype(int)
    # restaura a coluna de respostas
    msr[:, 0] = mensagens[:, 0]
    # subtotais de cada resposta
    unq, unq_inv = np.unique(msr[:, 0], return_inverse=True)
    out = np.zeros((len(unq), msr.shape[1]), dtype=mensagens.dtype)
    out[:, 0] = unq
    # cada palavra: total de cada resposta = 0
    np.add.at(out[:, 1:], unq_inv, msr[:, 1:])
    if debug: print('respostas 0: \n', out)
    # gini cada palavra com resposta: [(total de cada resposta = 1) / (total de respostas)] ** 2
    gini_sem_resposta = 1 - np.sum(np.power((out[:, 1:]).astype(dtype=float) / q_mens, 2), axis=0)
    if debug: print('gini sem resposta: \n', gini_sem_resposta)
    # obter a média ponderada
    qmp1 = (mensagens[:, 1:] == 1.0).sum(axis=0, dtype=float)
    qmp0 = (mensagens[:, 1:] == 0.0).sum(axis=0, dtype=float)
    g1 = np.column_stack((gini_com_resposta, gini_sem_resposta))
    w = np.column_stack((qmp1, qmp0))
    gini_palavras = gini_mensagens - ( 1 - np.average(g1, axis=1, weights=w))
    if debug: print('gini palavras: \n', gini_palavras)
    # para usar o menor gini
    #indice_melhor_palavra = np.argmin(gini_palavras)
    # para usar o maior gini
    indice_melhor_palavra = np.argmax(gini_palavras)
    melhor_palavra = palavras[indice_melhor_palavra + 1]
    if debug: print('melhor palavra e indice: \n', melhor_palavra, ' - ', indice_melhor_palavra)
    return [melhor_palavra, indice_melhor_palavra]


def escolher_melhor_palavra_gini_uma_resposta(mensagens, palavras, debug=False):
    q_mens = np.shape(mensagens)[0]
    # escolher uma resposta para iniciar o processo:
    #  a resposta com maior número de ocorrências.
    respostas, contagem = np.unique(mensagens[:, 0], return_counts=True)
    respostas_agrupadas = np.column_stack((respostas, contagem))
    #  selecionar maior resposta agrupada
    resposta_escolhida = respostas_agrupadas[np.argmax(respostas_agrupadas[:, 1:]), 0]
    if debug: print(' Reposta escolhida: ', resposta_escolhida);

    # calculando gini de O (O = conjunto de mensagens e suas respostas)
    resposta_escolhida_mensagens = mensagens[mensagens[:, 0] == resposta_escolhida]
    if debug: print('conjunto de mensagens apenas com a resposta escolhida')
    if debug: print(resposta_escolhida_mensagens)
    q_mens_resp_esc = np.shape(resposta_escolhida_mensagens)[0]
    if debug: print('quantidade de mensagens com a resposta escolhida: ', q_mens_resp_esc)
    # taxa de mensagens com a resposta escolhida (C)
    t_mens_resp_esc = dividir(q_mens_resp_esc, q_mens);
    if debug: print('taxa de mensagens com a resposta escolhida: ', t_mens_resp_esc);
    # taxa de mensagens sem a resposta escolhida (A)
    t_mens_sem_resp_esc = dividir((q_mens - q_mens_resp_esc), q_mens);
    if debug: print('taxa de mensagens sem a resposta escolhida: ', t_mens_sem_resp_esc);
    giniO = 1 - (pow(t_mens_resp_esc, 2) + pow(t_mens_sem_resp_esc, 2));
    # gini negativo não faz sentido ...
    giniO = max(0, giniO);
    if debug: print('GINI de O: ', giniO);
    # calculando o gini de cada palavra
    #  mensagens com cada palavra avaliada e qualquer resposta
    vet_q_mens_pal_aval = (mensagens[:, 1:] == 1.0).sum(axis=0, dtype=float)
    if debug: print('mensagens com cada palavra avaliada e qualquer resposta:')
    if debug: print(vet_q_mens_pal_aval)
    # quantidade de mensagens com a resposta escolhida com cada palavra
    vet_q_mens_resp_esc_pal_aval = (resposta_escolhida_mensagens[:, 1:] == 1.0).sum(axis=0, dtype=float)
    if debug: print('mensagens com cada palavra e a resposta escolhida:')
    if debug: print(vet_q_mens_resp_esc_pal_aval)
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
    vet_t_q_mens_resp_esc_pal_aval = \
        np.divide(vet_q_mens_resp_esc_pal_aval, vet_q_mens_pal_aval, out=np.zeros_like(vet_q_mens_resp_esc_pal_aval), \
                  where=vet_q_mens_pal_aval != 0.0, casting='unsafe')
    if debug: print('taxa de mensagens com cada palavra e a resposta escolhida:')
    if debug: print(vet_t_q_mens_resp_esc_pal_aval)
    # taxa de mensagens com a palavra sendo analisada e a resposta diferente da escolhida
    vet_q_mens_sem_resp_esc_pal_aval = vet_q_mens_pal_aval - vet_q_mens_resp_esc_pal_aval
    vet_t_q_mens_sem_resp_esc_pal_aval = \
        np.divide(vet_q_mens_sem_resp_esc_pal_aval, vet_q_mens_pal_aval,
                  out=np.zeros_like(vet_q_mens_sem_resp_esc_pal_aval), \
                  where=vet_q_mens_pal_aval != 0.0, casting='unsafe')
    if debug: print('taxa de mensagens com cada palavra e resposta diferente da escolhida:')
    if debug: print(vet_t_q_mens_sem_resp_esc_pal_aval)
    # gini das mensagens com cada palavra e com a resposta escolhida
    vet_gini_mens_pal_resposta_escolhida = \
        1 - (pow(vet_t_q_mens_resp_esc_pal_aval, 2) + pow(vet_t_q_mens_sem_resp_esc_pal_aval, 2));
    # gini negativo não faz sentido, zera
    # pode ser utilizado o método clip, exemplo:
    # a: [-1.  2. -5.  9. -3.]
    # a.clip(min=0)
    # [ 0.  2.  0.  9.  0.]
    # No entanto:
    # a *= (a>0)
    # [-0.  2. -0.  9. -0.]
    vet_gini_mens_pal_resposta_escolhida = vet_gini_mens_pal_resposta_escolhida.clip(min=0)
    if debug: print('gini das mensagens com cada palavra e com a resposta escolhida:')
    if debug: print(vet_gini_mens_pal_resposta_escolhida)

    #  mensagens sem cada palavra avaliada e qualquer resposta
    vet_q_mens_sem_pal_aval = (mensagens[:, 1:] == 0).sum(axis=0, dtype=float)
    # quantidade de mensagens com a resposta escolhida sem cada palavra
    vet_q_mens_resp_esc_sem_pal_aval = (resposta_escolhida_mensagens[:, 1:] == 0).sum(axis=0, dtype=float)
    if debug: print('mensagens com a resposta escolhida e sem cada palavra:')
    if debug: print(vet_q_mens_resp_esc_sem_pal_aval)
    # taxa de mensagens sem a palavra sendo analisada e com resposta escolhida
    vet_t_q_mens_resp_esc_sem_pal_aval = np.divide(vet_q_mens_resp_esc_sem_pal_aval, vet_q_mens_sem_pal_aval, \
                                                   out=np.zeros_like(vet_q_mens_resp_esc_sem_pal_aval),
                                                   where=vet_q_mens_sem_pal_aval != 0, casting='unsafe')
    if debug: print('taxa de mensagens com a resposta escolhida e sem cada palavra:')
    if debug: print(vet_t_q_mens_resp_esc_sem_pal_aval)
    # taxa de mensagens sem cada palavra sendo avaliada e resposta diferente da escolhida
    vet_q_mens_sem_resp_esc_sem_pal_aval = vet_q_mens_sem_pal_aval - vet_q_mens_resp_esc_sem_pal_aval
    vet_t_q_mens_sem_resp_esc_sem_pal_aval = np.divide(vet_q_mens_sem_resp_esc_sem_pal_aval, vet_q_mens_sem_pal_aval, \
                                                       out=np.zeros_like(vet_q_mens_sem_resp_esc_sem_pal_aval),
                                                       where=vet_q_mens_sem_pal_aval != 0, casting='unsafe')
    if debug: print('taxa de mensagens sem cada palavra sendo avaliada e resposta diferente da escolhida:')
    if debug: print(vet_t_q_mens_sem_resp_esc_sem_pal_aval)
    # gini das mensagens sem cada palavra sendo avaliada e sem a resposta escolhida
    vet_gini_q_mens_sem_pal_aval_sem_resp_esc = 1 - (
            pow(vet_t_q_mens_resp_esc_sem_pal_aval, 2) + pow(vet_t_q_mens_sem_resp_esc_sem_pal_aval, 2));
    # gini negativo não faz sentido, zera
    vet_gini_q_mens_sem_pal_aval_sem_resp_esc = vet_gini_q_mens_sem_pal_aval_sem_resp_esc.clip(min=0)
    if debug: print('gini das mensagens sem cada palavra sendo avaliada e sem a resposta escolhida:')
    if debug: print(vet_gini_q_mens_sem_pal_aval_sem_resp_esc)

    # calculando o gini de cada palavra
    vet_gini_pal_aval = giniO - ((vet_gini_mens_pal_resposta_escolhida * vet_q_mens_pal_aval / q_mens) + \
                                 (vet_gini_q_mens_sem_pal_aval_sem_resp_esc * vet_q_mens_sem_pal_aval / q_mens))
    # gini negativo não faz sentido, zera
    vet_gini_pal_aval = vet_gini_pal_aval.clip(min=0)
    if debug: print('Gini de cada palavra avaliada:')
    if debug: print(vGiniPalAval)

    # melhor palavra: a palavra com o maior GINI
    # TODO ValueError: attempt to get argmax of an empty sequence
    try:
        ind_pal_esc = np.argmax(vet_gini_pal_aval)
        pal_esc = palavras[ind_pal_esc + 1]
    except ValueError:
        # provisoriamente vamos pegar a primeira palavra disponivel
        pal_esc = [1]
        ind_pal_esc = 0
    return [pal_esc, ind_pal_esc]


def escolher_melhor_palavra_divisao_maxima(mensagens, palavras, debug=False):
    # subtotais cada resposta
    indice_melhor_palavra = np.argmax(np.sum(mensagens[:, 1:], axis=0))
    melhor_palavra = palavras[indice_melhor_palavra + 1]
    if debug: print('melhor palavra e indice: \n', melhor_palavra, ' - ', indice_melhor_palavra)
    return [melhor_palavra, indice_melhor_palavra]


def testar_arvore(arvore, testes, palavras, debug=False):
    acertos = 0
    erros = 0
    sem_respostas = 0
    testadas = 0
    # quantidade de mensagens a testar
    qmensteste = np.size(testes, 0)
    if debug:
        print('mensagens no conjunto de mensagens: ', qmensteste)
    for i in range(qmensteste):
        mensagem = testes[i]
        # pesquisar a arvore gerada iniciando pela raiz
        proximo = [0]
        while len(proximo) > 0:
            ind = proximo.pop(0)
            no = arvore.get(ind)
            if debug: print('No: ', ind)
            if not no.efolha:
                # verifica se a mensagem tem a
                # palavra da arvore ou não.
                palno = no.retpalavra
                if mensagem[palavras.index(palno)] == 1:
                    # mensagem tem a palavra
                    # vai para a esquerda
                    proximo.append(ind * 2 + 1)
                else:
                    # mensagem não tem a palavra
                    # vai para a direita
                    proximo.append(ind * 2 + 2)
            else:
                # hora da decisão
                if no.retrespostas is None or len(no.retrespostas) == 0:
                    sem_respostas += 1
                elif mensagem[0] == no.retrespostas[0]:
                    acertos += 1
                else:
                    erros += 1
                    # relatório de erro
                    if debug: print('!' * 79)
                    if debug: print("erro na classificação:")
                    if debug: print('Na mensagem da posição: ', i)
                    if debug: print("resposta esperada: ", mensagem[0])
                    if no.retrespostas is None or len(no.retrespostas) == 0:
                        if debug: print('resposta obtida: nenhuma!')
                    else:
                        if debug: print('resposta obtida: ', no.retrespostas[0])
                    if debug: print('!' * 79)

                testadas += 1
                if debug: print('testadas: ', testadas, ' acertos: ', acertos,
                                ' erros: ', erros, 'sem resposta: ', sem_respostas)
                if debug: print('acuidade: ', acertos * 100 / (acertos + erros))
                # parte para a próxima pesquisa
    return testadas, acertos, erros, sem_respostas

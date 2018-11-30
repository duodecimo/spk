#modulos

from timeit import default_timer as timer
import numpy as np
from datetime import datetime
import pickle
import pathlib
import sys

# classes

class nodados:

    
    # possui atributos para processar e gerar o no da arvore
    def __init__(self, indice, palavras, mensagens):
        self.__indice = indice          # vai ser o indice do dicionario arvore
        self.__palavra = None           # a melhor palavra que divide os nós
        self.__respostas = None         # lista de respostas
        self.__mensagens = mensagens    # matriz de mensagens a serem processadas
        self.__palavras = palavras      # vetor de palavras a serem processadas
        self.__folha = False            # indica se um nó é ou não folha

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


class no():

    # é o objeto do dicionário árvore
    # recebe como parâmetro um objeto nodados,
    # de onde extrai todos seus atributos
    def __init__(self, nodados_ob):
        self.__palavra = nodados_ob.retpalavra   # utilizada para dividir a árvore, ausente em folhas
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

def dividir(x, y):
    if y==0: return 0
    return x/y

def salvar_arvore(arvore, caminho):
    comp = datetime.now().strftime('%Y_%m_%d_%H_%M_%S_%f')[:-2]
    # utiliza a forma arvore_<timestamp>.pkl para o arquivo,
    # garantindo a unicidade do nome em seguidas
    # execuções do programa.
    nome_arq =  caminho +  'arvore_' + comp + '.pkl'
    # utiliza apenas arvore.pfl para o arquivo,
    # sempre sobrescrevendo o anterior, garantindo
    # desta forma acesso com um nome garantido
    # à última árvore gerada.
    nome_arq2 =  caminho +  'arvore.pkl'
    arq = open(nome_arq,'wb')
    pickle.dump(arvore, arq, pickle.HIGHEST_PROTOCOL)
    arq.close()
    try:
        pathlib.Path(nome_arq2).unlink()
    except FileNotFoundError:
        pass
    arq = open(nome_arq2,'wb')
    pickle.dump(arvore, arq, pickle.HIGHEST_PROTOCOL)
    arq.close()
    return nome_arq

def carregar_arvore(caminho, arq='arvore.pkl'):
    arqref = open(arq,'rb')
    arvore = pickle.load(arqref)
    arqref.close()
    return arvore

def dividir_arvore(arvore):
    n = len(arvore) // 2
    i = iter(arvore.items())      # alternatively, i = d.iteritems() works in Python 2

    arvore1 = dict(itertools.islice(i, n))   # grab first n items
    arvore2 = dict(i)                        # grab the rest

    return arvore1, arvore2


def calcula_no(nodados_ob, debug=False):
    #global inicio
    #global debug
    #global py
    #global qmaxmens

    indice = nodados_ob.retindice
    palavras = nodados_ob.retpalavras
    mensagens = nodados_ob.retmensagens

    fim = timer()
    q_mens = np.shape(mensagens)[0]
    
    #if q_mens > qmaxmens:
    #    qmaxmens = q_mens

    if debug:
        usoMemoria = py.memory_info()[0]/2.**30  # memory use in GB...I think
        print('uso de memoria:', usoMemoria)
        print('')
        print('Ate o no ', indice, ': ')
        print(' tempo (em segundos): ', str(timedelta(seconds=fim - inicio)))
        #print('quantidade de mensagens: ', q_mens)
        print('-'*79)

    # escolher melhor palavra
    #[pal_esc, ind_pal_esc] = escolher_melhor_palavra_antigo(mensagens, palavras, q_mens, debug)
    [pal_esc, ind_pal_esc] = escolher_melhor_palavra(mensagens, palavras, q_mens, debug=False)

    # inserir nos dados do nó a palavra que divide a árvore
    nodados_ob.inspalavra(pal_esc)
    if debug: print('Melhor palavra: ', pal_esc, ' indice: ', ind_pal_esc +1)
    if debug: print('conferindo palavra do no: ', nodados_ob.retpalavra)
    # dividir as mensagens entre as que contém a palavra com melhor GINI e as que não.
    mensagensPalAval = mensagens[mensagens[:, ind_pal_esc+1]==1]
    mensagens_PalAval = mensagens[mensagens[:, ind_pal_esc+1]==0]
    if debug: print('mensagens que contém a melhor palavra:')
    if debug: print(mensagensPalAval)
    if debug: print('mensagens sem a melhor palavra:')
    if debug: print(mensagens_PalAval)
    # remove a palavra dos novos conjuntos de mensagens (esquerdo e direito)
    mensagensPalAval = np.delete(mensagensPalAval, [ind_pal_esc+1], axis=1)
    mensagens_PalAval = np.delete(mensagens_PalAval, [ind_pal_esc+1], axis=1)
    # é preciso verificar a invariância das mensagens:
    # comparemos as quantidades de linhas
    if not np.size(mensagens, 0) == np.size(mensagensPalAval, 0) + np.size(mensagens_PalAval, 0):
        print('*'*79)
        print('-'*79)
        print('Erro de invariância no nó ', nodados_ob.retindice)
        print('pai: ', np.size(mensagens, 0))
        print('esq: ', np.size(mensagensPalAval, 0))
        print('dir: ', np.size(mensagens_PalAval, 0))
        print('*'*79)
        print('-'*79)
        raise  Exception('Divisão de dados com falha!')
    # ajusta a lista de palavras para os nós filhos (esquerdo e direito)
    palavrasProxno = np.delete(palavras, [ind_pal_esc+1])
    if debug: print('palavras proximo no:')
    if debug: print(palavrasProxno)
    # inicia o calculo dos dados de nós ou folhas
    # à esquerda e a direata que serão retornados.

    # nodados(indice, palavras, mensagens)
    nodados_ob_esq = nodados(indice*2+1, palavrasProxno, mensagensPalAval)
    nodados_ob_dir = nodados(indice*2+2, palavrasProxno, mensagens_PalAval)
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
    nodados_esq_resp = np.unique(mensagensPalAval[:,0])
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
    if np.size(nodados_esq_resp) < 2 or np.size(mensagensPalAval, 0) <2 \
        or np.size(mensagensPalAval, 1) <2:
        # np.size(nodados_esq_resp) dá o número de respostas.
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
        nodados_ob_esq.atribfolha(True)
        # colocamos as respostas na folha (e somente nelas)
        # vão ser sempre vetores, no caso ideal, com apenas
        # um valor.
        if np.size(nodados_esq_resp) > 0:
            nodados_ob_esq.insrespostas(nodados_esq_resp)
            if debug: print('folha com resposta(s): ', nodados_esq_resp, \
            ' a esquerda do no ', indice)
        else:
            # o ideal é quando a folha tem uma resposta,
            # mas, se não tiver:
            # colocamos as respotas do no pai
            nodados_ob_esq.insrespostas(np.unique(mensagens[:,0]))
            if debug: print('folha com resposta(s) (do pai): ', \
            np.unique(mensagens[:,0]), ' a esquerda do no ', indice)
    # à direita
    # (obs.: as explicações são as mesmas dadas acima
    # para o processamento de expansão à esquerda).
    nodados_dir_resp = np.unique(mensagens_PalAval[:,0])
    if np.size(nodados_dir_resp) < 2 or np.size(mensagens_PalAval, 0) <2 \
        or np.size(mensagens_PalAval, 1) <2:
        nodados_ob_dir.atribfolha(True)
        if np.size(nodados_dir_resp) >0:
            nodados_ob_dir.insrespostas(nodados_dir_resp)
            if debug: print('folha com resposta(s): ', \
            nodados_dir_resp, ' a direita do no ', indice)
        else:
            nodados_ob_dir.insrespostas(np.unique(mensagens[:,0]))
            if debug: print('folha com resposta(s) (do pai): ', \
            np.unique(mensagens[:,0]), ' a direita do no ', indice)
    return (nodados_ob_esq, nodados_ob_dir)


def escolher_melhor_palavra_antigo(mensagens, palavras, q_mens, debug=False):


    # escolher uma resposta para iniciar o processo:
    #  a resposta com maior número de ocorrências.
    respostas, contagem = np.unique(mensagens[:,0], return_counts=True)
    respostas_agrupadas = np.column_stack((respostas,contagem))
    #  selecionar maior resposta agrupada
    resposta_escolhida = respostas_agrupadas[np.argmax(respostas_agrupadas[:,1:]), 0]
    if debug: print(' Reposta escolhida: ', resposta_escolhida);

    # calculando gini de O (O = conjunto de mensagens e suas respostas)
    resposta_escolhida_mensagens = mensagens[mensagens[:,0]==resposta_escolhida]
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
    vet_q_mens_pal_aval = (mensagens[:,1:]==1.0).sum(axis=0, dtype=float)
    if debug: print('mensagens com cada palavra avaliada e qualquer resposta:')
    if debug: print(vet_q_mens_pal_aval)
    # quantidade de mensagens com a resposta escolhida com cada palavra
    vet_q_mens_resp_esc_pal_aval = (resposta_escolhida_mensagens[:,1:]==1.0).sum(axis=0, dtype=float)
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
    where=vet_q_mens_pal_aval!=0.0, casting='unsafe')
    if debug: print('taxa de mensagens com cada palavra e a resposta escolhida:')
    if debug: print(vet_t_q_mens_resp_esc_pal_aval)
    # taxa de mensagens com a palavra sendo analisada e a resposta diferente da escolhida
    vet_q_mens_sem_resp_esc_pal_aval = vet_q_mens_pal_aval - vet_q_mens_resp_esc_pal_aval
    vet_t_q_mens_sem_resp_esc_pal_aval = \
    np.divide(vet_q_mens_sem_resp_esc_pal_aval, vet_q_mens_pal_aval, out=np.zeros_like(vet_q_mens_sem_resp_esc_pal_aval), \
    where=vet_q_mens_pal_aval!=0.0, casting='unsafe')
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
    # no entanto:
    # a *= (a>0)
    # [-0.  2. -0.  9. -0.]
    vet_gini_mens_pal_resposta_escolhida = vet_gini_mens_pal_resposta_escolhida.clip(min=0)
    if debug: print('gini das mensagens com cada palavra e com a resposta escolhida:')
    if debug: print(vet_gini_mens_pal_resposta_escolhida)

    #  mensagens sem cada palavra avaliada e qualquer resposta
    vet_q_mens_sem_pal_aval = (mensagens[:,1:]==0).sum(axis=0, dtype=float)
    # quantidade de mensagens com a resposta escolhida sem cada palavra
    vet_q_mens_resp_esc_sem_pal_aval = (resposta_escolhida_mensagens[:,1:]==0).sum(axis=0, dtype=float)
    if debug: print('mensagens com a resposta escolhida e sem cada palavra:')
    if debug: print(vet_q_mens_resp_esc_sem_pal_aval)
    # taxa de mensagens sem a palavra sendo analisada e com resposta escolhida
    vet_t_q_mens_resp_esc_sem_pal_aval = np.divide(vet_q_mens_resp_esc_sem_pal_aval, vet_q_mens_sem_pal_aval, \
     out=np.zeros_like(vet_q_mens_resp_esc_sem_pal_aval), where=vet_q_mens_sem_pal_aval!=0, casting='unsafe')
    if debug: print('taxa de mensagens com a resposta escolhida e sem cada palavra:')
    if debug: print(vet_t_q_mens_resp_esc_sem_pal_aval)
    # taxa de mensagens sem cada palavra sendo avaliada e resposta diferente da escolhida
    vet_q_mens_sem_resp_esc_sem_pal_aval = vet_q_mens_sem_pal_aval - vet_q_mens_resp_esc_sem_pal_aval
    vet_t_q_mens_sem_resp_esc_sem_pal_aval = np.divide(vet_q_mens_sem_resp_esc_sem_pal_aval, vet_q_mens_sem_pal_aval, \
     out=np.zeros_like(vet_q_mens_sem_resp_esc_sem_pal_aval), where=vet_q_mens_sem_pal_aval!=0, casting='unsafe')
    if debug: print('taxa de mensagens sem cada palavra sendo avaliada e resposta diferente da escolhida:')
    if debug: print(vet_t_q_mens_sem_resp_esc_sem_pal_aval)
    # gini das mensagens sem cada palavra sendo avaliada e sem a resposta escolhida
    vet_gini_q_mens_sem_pal_aval_sem_resp_esc = 1 - (pow(vet_t_q_mens_resp_esc_sem_pal_aval, 2) + pow(vet_t_q_mens_sem_resp_esc_sem_pal_aval, 2));
    # gini negativo não faz sentido, zera
    vet_gini_q_mens_sem_pal_aval_sem_resp_esc = vet_gini_q_mens_sem_pal_aval_sem_resp_esc.clip(min=0)
    if debug: print('gini das mensagens sem cada palavra sendo avaliada e sem a resposta escolhida:')
    if debug: print(vet_gini_q_mens_sem_pal_aval_sem_resp_esc)

    # calculando o gini de cada palavra
    vet_gini_pal_aval= giniO - ((vet_gini_mens_pal_resposta_escolhida * vet_q_mens_pal_aval / q_mens) + \
    (vet_gini_q_mens_sem_pal_aval_sem_resp_esc * vet_q_mens_sem_pal_aval / q_mens))
    # gini negativo não faz sentido, zera
    vet_gini_pal_aval= vet_gini_pal_aval.clip(min=0)
    if debug: print('Gini de cada palavra avaliada:')
    if debug: print(vGiniPalAval)

    # melhor palavra: a palavra com o maior GINI
    # TODO ValueError: attempt to get argmax of an empty sequence
    try:
        ind_pal_esc = np.argmax(vet_gini_pal_aval)
        pal_esc = palavras[ind_pal_esc +1]
    except ValueError:
        # provisoriamente vamos pegar a primeira palavra disponivel
        pal_esc = [1]
        ind_pal_esc = 0
    return [pal_esc, ind_pal_esc]

def escolher_melhor_palavra(mensagens, palavras, q_mens, debug=False):

    superdebug = True
    # para cada palavra
    
    # com resposta
    # subtotaliza cada resposta
    unq, unq_inv = np.unique(mensagens[:, 0], return_inverse=True)
    out = np.zeros((len(unq), mensagens.shape[1]), dtype=mensagens.dtype)
    out[:, 0] = unq
    # cada palavra: total de cada resposta = 1
    np.add.at(out[:, 1:], unq_inv, mensagens[:, 1:])
    if superdebug: print('respostas 1: \n', out)
    # gini cada palavra com resposta: [(total de cada resposta = 1) / (total de respostas)] ** 2
    gini_com_resposta = 1 - np.sum(np.power(np.divide(out[:, 1:], q_mens, dtype=float), 2), axis=0)
    if superdebug: print('gini com resposta: \n', gini_com_resposta)
    # sem resposta
    # troca zeros por um e vice versa nos valores, att: danifica a coluna de respostas
    msr = np.logical_not(mensagens).astype(int)
    # restaura a coluna de respostas
    msr[:, 0] = mensagens[:, 0]
    # subtotaliza cada resposta
    unq, unq_inv = np.unique(msr[:, 0], return_inverse=True)
    out = np.zeros((len(unq), msr.shape[1]), dtype=mensagens.dtype)
    out[:, 0] = unq
    # cada palavra: total de cada resposta = 0
    np.add.at(out[:, 1:], unq_inv, msr[:, 1:])
    if superdebug: print('respostas 0: \n', out)
    # gini cada palavra com resposta: [(total de cada resposta = 1) / (total de respostas)] ** 2
    gini_sem_resposta = 1 - np.sum(np.power(np.divide(out[:, 1:], q_mens, dtype=float), 2), axis=0)
    if superdebug: print('gini sem resposta: \n', gini_sem_resposta)
    # obter a média ponderada
    qmp1 = (mensagens[:,1:]==1.0).sum(axis=0, dtype=float)
    qmp0 = (mensagens[:,1:]==0.0).sum(axis=0, dtype=float)
    g1 = np.column_stack((gini_com_resposta, gini_sem_resposta))
    w = np.column_stack((qmp1, qmp0))
    gini_palavras = np.average(g1, axis=1, weights=w)
    if superdebug: print('gini palavras: \n', gini_palavras)
    indice_melhor_palavra = minval = np.argmin(gini_palavras)
    melhor_palavra = palavras[indice_melhor_palavra+1]
    if superdebug: print('melhor palavra e indice: \n', melhor_palavra, ' - ', indice_melhor_palavra)
    sys.exit()
    return [melhor_palavra, indice_melhor_palavra]



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
    def __init__(self, nodados):
        self.__palavra = nodados.retpalavra   # utilizada para dividir a árvore, ausente em folhas
        self.__respostas = nodados.retrespostas
        self.__folha = nodados.efolha

    @property
    def retpalavra(self):
        return self.__palavra

    @property
    def retrespostas(self):
        return self.__respostas

    @property
    def efolha(self):
        return self.__folha


class nodados:
    # possui atributos para processar e gerar o No da arvore

    def __init__(self, indice, palavras, mensagens):
        self.__indice = indice    # vai ser o índice do dicionario arvore
        self.__palavra = None # a melhor palavra que divide os nós
        self.__respostas = None   # uma lista de respostas, para os nós folha, idealmente apenas uma resposta
        self.__mensagens = mensagens  # matriz de mensagens a serem processadas
        self.__palavras = palavras    # vetor de palavras a serem processadas
        self.__folha = False  # indica se um nó é ou não folha

    def retindice(self):
        return self.__indice

    def inspalavra(self, palavra):
        self.__palavra = palavra

    def retpalavra(self):
        return self.__palavra

    def insrespostas(self, respostas):
        self.__respostas = respostas

    def retrespostas(self):
        return self.__respostas

    def insmensagens(self, mensagens):
        self.__mensagens = mensagens

    def retmensagens(self):
        return self.__mensagens

    def retpalavras(self):
        return self.__palavras

    def atribfolha(self, val):
        self.__folha = val

    def efolha(self):
        return self.__folha


class no:
    # é o objeto do dicionário árvore

    def __init__(self, nodados):    # recebe como parâmetro um noDados, de onde extrai todos seus atributos
        self.__palavra = nodados.retpalavra()    # utilizada para dividir a árvore, pode não existir em folhas
        self.__respostas = nodados.retrespostas()
        self.__folha = nodados.efolha

    @property
    def retpalavra(self):
        return self.__palavra + ' (protegida)'

    @property
    def retrespostas(self):
        return self.__respostas

    @property
    def efolha(self):
        return self.__folha


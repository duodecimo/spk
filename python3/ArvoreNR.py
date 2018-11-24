#!/bin/python

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

    # teste
    #noDados = NoDados(indice, palavras, mensagens)
    # cria o no raiz
    noDados = NoDados(0, ['ALO', 'ESQUERDA', 'DIREITA', 'EE', 'ED', 'DE', 'DD'], [[10,0,1,1],[20, 1,1,0]])
    print('raiz a processar:')
    print(noDados.retIndice(), ' - ', noDados.retPalavra())

    # calcula no
    noDados.insPalavra('ALO')
    # retorna filhos
    noDadosE = NoDados((2*noDados.retIndice())+1, noDados.retPalavras().remove('ALO'), noDados.retMensagens())
    noDadosD = NoDados((2*noDados.retIndice())+2, noDados.retPalavras(), noDados.retMensagens())
    #ins em nos a processar
    filaDeNos.append(noDadosE)
    filaDeNos.append(noDadosD)
    #ins na arvore o no processado
    arvore[noDados.retIndice()] = No(noDados)
    # recupera no a processar
    noDados = filaDeNos.pop()
    print('no recuperado:')
    print(noDados.retIndice(), ' - ', noDados.retPalavra())

    # calcula no
    noDados.insPalavra('ESQUERDA')
    # retorna filhos
    noDadosE = NoDados(2*noDados.retIndice()+1, noDados.retPalavras().remove('ESQUERDA'), noDados.retMensagens())
    noDadosD = NoDados(2*noDados.retIndice()+2, noDados.retPalavras(), noDados.retMensagens())
    #ins em nos a processar
    filaDeNos.append(noDadosE)
    filaDeNos.append(noDadosD)
    #ins na arvore o no processado
    arvore[noDados.retIndice()] = No(noDados)
    # recupera no a processar
    noDados = filaDeNos.pop()
    print('no recuperado:')
    print(noDados.retIndice(), ' - ', noDados.retPalavra())

    # calcula no
    noDados.insPalavra('DIREITA')
    # retorna filhos
    noDadosE = NoDados(2*noDados.retIndice()+1, noDados.retPalavras().remove('DIREITA'), noDados.retMensagens())
    noDadosD = NoDados(2*noDados.retIndice()+2, noDados.retPalavras(), noDados.retMensagens())
    #ins em nos a processar
    filaDeNos.append(noDadosE)
    filaDeNos.append(noDadosD)
    #ins na arvore o no processado
    arvore[noDados.retIndice()] = No(noDados)

    #para teste, tá bom
    print('arvore:')
    print(arvore.get(0).Palavra())
    print(arvore.get(2).Palavra())
    print(arvore.get(6).Palavra())

if __name__ == "__main__":
    main()


import numpy as np

mensagens = np.array(
[[1, 0, 1, 1, 0, 0],
 [2, 1, 1, 0, 0, 0],
 [3, 1, 0, 0, 1, 1],
 [4, 0, 0, 1, 0, 1],
 [1, 0, 1, 1, 0, 0],
 [2, 1, 1, 0, 0, 1],
 [1, 1, 1, 1, 0, 0]])

print('# Construuí este código para conferir o cálculo do método')
print('#  que chamei de gini total.')
print('#  Não creio ser nescessário ter conhecimento da linguagem')
print('#  Python e das rotinas da biblioteca Numpy, principalmente')
print('#  a vetorização dos cálculos. Basta ler pulando os comandos:')
print('#  basta ver os comentários e resultados.')

print('# A matriz mensagens é um pequeno modelo dos dados de treino.')
print('# Cada linha representa uma mensagem.')
print('# A primeira coluna representa as respostas.')
print('# Cada coluna subsequente representa uma palavra,')
print('#  que existe (valor = 1) ou não (valor = 0) na mensagem.')
print('mensagens:')
print(mensagens)
print('confere!')

print('# A quantidade de mensagens')
print('q_mens = np.shape(mensagens)[0]')
q_mens = np.shape(mensagens)[0]
print('q_mens: ')
print(q_mens)
print('confere!')

print('# vetor de subtotais cada resposta')
print('_, vet_sub_tot_resps = np.unique(mensagens[:, 0], return_counts=True')
_, vet_sub_tot_resps = np.unique(mensagens[:, 0], return_counts=True)
print('vet_sub_tot_resps: ')
print(vet_sub_tot_resps)
print('confere!')

print('# a quantidade de respostas, nossas classes.')
print('tot_resps = np.sum(vet_sub_tot_resps)')
tot_resps = np.sum(vet_sub_tot_resps)
print('tot_resps: ')
print(tot_resps)
print('confere!')

print('# Vetor de probabilidade de cada resposta | total de respostas')
print('sum_probs_resps = np.power(vet_sub_tot_resps.astype(dtype=float) / tot_resps, 2)')
print('#  (3÷7)^2=0,1837, (2÷7)^2=0,0816,(1÷7)^2=0,0204,(1÷7)^2=0,0204')
sum_probs_resps = np.power(vet_sub_tot_resps.astype(dtype=float) / tot_resps, 2)
print('sum_probs_resps: ')
print(sum_probs_resps)
print('confere!')

print('# Gini do conjunto de mensagens.')
print('gini_mensagens = 1 - np.sum(sum_probs_resps)')
gini_mensagens = 1 - np.sum(sum_probs_resps)
print('gini_mensagens: ')
print(gini_mensagens)
print('#  0,1837 + 0,0816 + 0,0204 + 0,0204=0,3061')
print('#  1 - 0,3061=0,6939')
print('confere!')

print('# para cada palavra:')

print('# com alguma resposta:')
# subtotais de cada resposta
unq, unq_inv = np.unique(mensagens[:, 0], return_inverse=True)
out = np.zeros((len(unq), mensagens.shape[1]), dtype=mensagens.dtype)
out[:, 0] = unq
print('# cada palavra: total de cada resposta = 1.')
np.add.at(out[:, 1:], unq_inv, mensagens[:, 1:])
print('respostas 1: \n', out)
print('confere!')

print('# gini cada palavra com resposta: [(total de cada resposta = 1) / (total de respostas)] ** 2')
print('gini_com_resposta = 1 - np.sum(np.power((out[:, 1:]).astype(dtype=float) / q_mens, 2), axis=0)')
gini_com_resposta = 1 - np.sum(np.power((out[:, 1:]).astype(dtype=float) / q_mens, 2), axis=0)
print('# primeira palavra: (palavras começam na segunda coluna.')
print('#  (1÷7)²=0,0204')
print('#  (2÷7)²=0,0816')
print('#  (1÷7)²=0,0204')
print('#  (0÷7)²=0')
print('#  0,0204+0,0816+0,0204+0=0,1224')
print('#  1−0,1224=0,8776')
print('# mesmo calculo para as outras palavras')
print('gini com resposta: \n', gini_com_resposta)
print('confere!')

print('# sem resposta (o valor para a resposta é 0.')
print('# troca zeros por um e vice versa nos valores, (att: danifica potencialmente a coluna de respostas)')
msr = np.logical_not(mensagens).astype(int)
print('# restaura a coluna de respostas.')
msr[:, 0] = mensagens[:, 0]
print('# subtotais de cada resposta.')
unq, unq_inv = np.unique(msr[:, 0], return_inverse=True)
out = np.zeros((len(unq), msr.shape[1]), dtype=mensagens.dtype)
out[:, 0] = unq
print('# cada palavra: total de cada resposta = 0.')
np.add.at(out[:, 1:], unq_inv, msr[:, 1:])
print('respostas 0: \n', out)
print('# é só observar que vai ser o complemento das respostas 1.')
print('# ou seja, nomero de respostas - numero de respostas 1.')
print('confere!')

print('# gini cada palavra com resposta: [(total de cada resposta = 1) / (total de respostas)] ** 2')

print('gini_sem_resposta = 1 - np.sum(np.power((out[:, 1:]).astype(dtype=float) / q_mens, 2), axis=0)')
gini_sem_resposta = 1 - np.sum(np.power((out[:, 1:]).astype(dtype=float) / q_mens, 2), axis=0)
print('gini sem resposta: \n', gini_sem_resposta)
print('# conferindo a primeira palavra (segunda coluna)')
print('#  (2÷7)²=0,0816')
print('#  (0÷7)²=0')
print('#  (0÷7)²=0')
print('#  (1÷7)²=0,0204')
print('#  0,0816+0+0+0,0204=0,102')
print('#  1−0,102=0,898')
print('confere!')

print('# obter a média ponderada.')
print('qmp1 = (mensagens[:, 1:] == 1.0).sum(axis=0, dtype=float)')
qmp1 = (mensagens[:, 1:] == 1.0).sum(axis=0, dtype=float)
print('qmp1')
print(qmp1)
print('# é só observar na matriz.')
print('confere!')

print('qmp0 = (mensagens[:, 1:] == 0.0).sum(axis=0, dtype=float)')
qmp0 = (mensagens[:, 1:] == 0.0).sum(axis=0, dtype=float)
print('qmp0')
print('# é o complemento do tamanho (7) com qmp1')
print(qmp0)
print('confere!')


print('g1 = np.column_stack((gini_com_resposta, gini_sem_resposta))')
g1 = np.column_stack((gini_com_resposta, gini_sem_resposta))
print(g1)
print('confere!')

print('w = np.column_stack((qmp1, qmp0))')
w = np.column_stack((qmp1, qmp0))
print('w: ')
print(w)
print('confere!')

print('np.average(g1, axis=1, weights=w)')
print(np.average(g1, axis=1, weights=w))

print('# Não confere: está dando valor negativo!!!!')
print('# tentando inverter a média (1 - ...)')
print('gini_palavras = gini_mensagens - (1 - np.average(g1, axis=1, weights=w))')
gini_palavras = gini_mensagens - (1 - np.average(g1, axis=1, weights=w))
print('confere!')

print('gini palavras: \n', gini_palavras)

print('# para usar o menor gini')
print('indice_melhor_palavra1 = np.argmin(gini_palavras)')
indice_melhor_palavra1 = np.argmin(gini_palavras)
print('indice_melhor_palavra1 (minimo): ')
print(indice_melhor_palavra1)

print('# para usar o maior gini: Esse é o que foi utilizado no programa.')
print('indice_melhor_palavra2 = np.argmax(gini_palavras)')
indice_melhor_palavra2 = np.argmax(gini_palavras)
print('indice_melhor_palavra2')
print(indice_melhor_palavra2)
print('# Fim da rotina.')


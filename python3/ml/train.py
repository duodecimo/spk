#imports

import csv
import numpy as np
from keras.models import Sequential
from keras.optimizers import Adam
from keras.callbacks import ModelCheckpoint
from keras.layers import Lambda, Conv2D, MaxPooling2D, Dropout, Dense, Flatten
from keras.callbacks import TensorBoard
from sklearn.model_selection import train_test_split
import os
import sys


def load_data():
    palavras = []
    mensagens = []
    np.random.seed(0)
    # ler o arquivo csv
    with open("../dados/Training.csv", encoding='iso-8859-1') as csvfile:
        reader = csv.reader(csvfile)
        palavras = next(reader, None)
        palavras = np.asarray(palavras)
        for mensagem in reader:
            mensagens.append(mensagem)
        mensagens = np.asarray(mensagens, dtype=np.dtype('uint32'))
    # shuffle
    np.random.seed(0)
    np.random.shuffle(mensagens)
    l = mensagens.shape[0]
    treinos, testes = mensagens[: int(l * .7)], mensagens[int(l * .7):]
    # inflate
    t = treinos
    for i in range(1):
        treinos = np.append(treinos, t, axis=0)
    np.random.shuffle(mensagens)
    # separate 1st column (answers) in each set
    X_train = treinos[:, 1:]
    y_train = treinos[:, 0]
    X_valid = testes[:, 1:]
    y_valid = testes[:, 0]
    labels = palavras[1:]
    print('>' * 79)
    print('Mensagens (', mensagens.shape, ') particionadas e infladas ', 2, ' vezes.')
    print(' treinos(', treinos.shape, ') e testes(', testes.shape, ')')
    print('>' * 79)

    return labels, X_train, X_valid, y_train, y_valid

def build_model(keep_prob, train_shape):
    model = Sequential()
    model.add(Lambda(lambda x: x/127.5-1.0, input_shape=train_shape))
    model.add(Conv2D(24, 5, 5, activation='elu', subsample=(2, 2)))
    model.add(Conv2D(36, 5, 5, activation='elu', subsample=(2, 2)))
    model.add(Conv2D(48, 5, 5, activation='elu', subsample=(2, 2)))
    model.add(Conv2D(64, 3, 3, activation='elu'))
    model.add(Conv2D(64, 3, 3, activation='elu'))
    model.add(Dropout(keep_prob))
    model.add(Flatten())
    model.add(Dense(100, activation='elu'))
    model.add(Dense(50, activation='elu'))
    model.add(Dense(10, activation='elu'))
    model.add(Dense(1))
    # let's change from Dense(1) to Dense(9, activation='softmax')
    # where 9 is the number of classes and softmax can be understood
    # here: https://en.wikipedia.org/wiki/Softmax_function
    # model.add(Dense(9, activation='softmax'))
    model.summary()

    return model

def train_model(model, psave_best_only, learning_rate, samples_per_epoch, nb_epoch, batch_size, X_train, X_valid, y_train, y_valid):
    """
    Train the model
    """
    checkpoint = ModelCheckpoint('model-{epoch:03d}.h5',
                                 monitor='val_loss',
                                 verbose=0,
                                 save_best_only=psave_best_only,
                                 mode='auto')

    model.compile(loss='categorical_crossentropy', optimizer=Adam(lr=learning_rate), metrics=['accuracy'])
    # adding a tensorboard callback
    '''
    model.fit_generator(batch_generator(X_train, y_train, batch_size, True),
                        samples_per_epoch,
                        nb_epoch,
                        max_q_size=1,
                        validation_data = batch_generator(X_valid, y_valid, batch_size, False),
                        nb_val_samples=len(X_valid),
                        callbacks=[checkpoint, 
                                   TensorBoard(log_dir='./logs/tensorboard')],
                        verbose=1)
    '''
    model.fit(X_train,
              y_train,
              samples_per_epoch,
              nb_epoch,
              validation_data =(X_valid, y_valid),
              callbacks=[checkpoint, TensorBoard(log_dir='./logs/tensorboard')],
              verbose=1)

def main():

    labels, X_train, X_valid, y_train, y_valid = load_data()

    print("Train Images: ", len(X_train))
    print("Valid Images: ", len(X_valid))
    print("Train Results: ", len(y_train))
    print("Valid Results: ", len(y_valid))
    
    #print("valid: x: ", X_valid, " y: ", y_valid) 
    #exit(1)

    # Let's build the model.

    keep_prob = 0.5
    train_shape = [X_train.shape[0], X_train.shape[1], 1]
    model = build_model(keep_prob, train_shape)


    # Let's train the model.

    psave_best_only = True
    learning_rate = 1.0e-4
    samples_per_epoch = 20000
    nb_epoch = 10
    batch_size = 40
    train_model(model, psave_best_only, learning_rate, samples_per_epoch, nb_epoch, batch_size, 
                X_train, X_valid, y_train, y_valid)

if __name__ == "__main__":
    main()

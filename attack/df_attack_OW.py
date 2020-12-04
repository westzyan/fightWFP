import pickle
import numpy as np
# from keras import backend as K
from Model_DF import DFNet
import random
import pandas as pd
from keras.utils import np_utils
from keras.optimizers import Adamax
import numpy as np
import os
import tensorflow as tf
import keras
config = tf.ConfigProto()
config.gpu_options.allow_growth = True
keras.backend.tensorflow_backend.set_session(tf.Session(config=config))
# Load data for non-defended dataset for CW setting
def LoadDataNoDefOW():
    print("Loading defended dataset for closed-world scenario")
    # Point to the directory storing data
    # dataset_dir = '../dataset/ClosedWorld/NoDef/'
    # dataset_dir = "/media/zyan/软件/张岩备份/PPT/DeepFingerprinting/df-master/dataset/ClosedWorld/NoDef/"
    dataset_dir = "/media/zyan/文档/毕业设计/code/dataset/round10/"
    # X represents a sequence of traffic directions
    # y represents a sequence of corresponding label (website's label)
    data = np.loadtxt(dataset_dir + "df_CW15000_OW_800.csv", delimiter=",")
    print(data)
    np.random.shuffle(data)
    print(data)
    print(len(data))
    train_length = int(0.8 * len(data))
    valid_length = int(0.1 * len(data))
    test_length = len(data) - train_length - valid_length
    train = data[:train_length, :]
    valid = data[train_length: train_length + valid_length, :]
    test = data[train_length + valid_length:, :]

    X_train = train[:, :-1]
    y_train = train[:,-1]
    X_valid = valid[:, :-1]
    y_valid = valid[:,-1]
    X_test = test[:, :-1]
    y_test = test[:,-1]

    print("X: Training data's shape : ", X_train.shape)
    print("y: Training data's shape : ", y_train.shape)
    print("X: Validation data's shape : ", X_valid.shape)
    print("y: Validation data's shape : ", y_valid.shape)
    print("X: Testing data's shape : ", X_test.shape)
    print("y: Testing data's shape : ", y_test.shape)
    #
    return X_train, y_train, X_valid, y_valid, X_test, y_test


# LoadDataNoDefCW()

if __name__ == '__main__':
    random.seed(0)
    os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'

    # Use only CPU
    # os.environ["CUDA_DEVICE_ORDER"] = "PCI_BUS_ID"   # see issue #152
    # os.environ["CUDA_VISIBLE_DEVICES"] = "1"

    description = "Training and evaluating DF model for closed-world scenario on non-defended dataset"

    print(description)
    # Training the DF model
    NB_EPOCH = 30  # Number of training epoch
    print("Number of Epoch: ", NB_EPOCH)
    BATCH_SIZE = 128  # Batch size
    VERBOSE = 2  # Output display mode
    LENGTH = 5000  # Packet sequence length
    OPTIMIZER = Adamax(lr=0.002, beta_1=0.9, beta_2=0.999, epsilon=1e-08, decay=0.0)  # Optimizer

    NB_CLASSES = 51  # number of outputs = number of classes
    INPUT_SHAPE = (LENGTH, 1)

    # Data: shuffled and split between train and test sets
    print("Loading and preparing data for training, and evaluating the model")
    X_train, y_train, X_valid, y_valid, X_test, y_test = LoadDataNoDefOW()
    # Please refer to the dataset format in readme
    # K.set_image_dim_ordering("tf") # tf is tensorflow

    # Convert data as float32 type
    X_train = X_train.astype('float32')
    X_valid = X_valid.astype('float32')
    X_test = X_test.astype('float32')
    y_train = y_train.astype('float32')
    y_valid = y_valid.astype('float32')
    y_test = y_test.astype('float32')

    # we need a [Length x 1] x n shape as input to the DF CNN (Tensorflow)
    X_train = X_train[:, :, np.newaxis]
    X_valid = X_valid[:, :, np.newaxis]
    X_test = X_test[:, :, np.newaxis]

    print(X_train.shape[0], 'train samples')
    print(X_valid.shape[0], 'validation samples')
    print(X_test.shape[0], 'test samples')
    # Convert class vectors to categorical classes matrices
    y_train = np_utils.to_categorical(y_train, NB_CLASSES)
    y_valid = np_utils.to_categorical(y_valid, NB_CLASSES)
    y_test = np_utils.to_categorical(y_test, NB_CLASSES)

    # Building and training model
    print("Building and training DF model")

    model = DFNet.build(input_shape=INPUT_SHAPE, classes=NB_CLASSES)

    model.compile(loss="categorical_crossentropy", optimizer=OPTIMIZER,
                  metrics=["accuracy"])
    print("Model compiled")

    # Start training
    history = model.fit(X_train, y_train,
                        batch_size=BATCH_SIZE, epochs=NB_EPOCH,
                        verbose=VERBOSE, validation_data=(X_valid, y_valid))

    # model.save('my_model_undef_tcp_10000_round2.h5')

    # Start evaluating model with testing data
    score_test = model.evaluate(X_test, y_test, verbose=VERBOSE)
    print("Testing accuracy:", score_test[1])


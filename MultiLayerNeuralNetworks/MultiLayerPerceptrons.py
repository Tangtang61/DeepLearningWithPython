#!/usr/bin/python
# -*- coding: utf-8 -*-
u"""
Copyright (c) 2016 Masaru Morita

This software is released under the MIT License.
See LICENSE file included in this repository.
"""

import random
import sys

sys.path.append('..')

from SingleLayerNeuralNetworks.LogisticRegression import LogisticRegression
from MultiLayerNeuralNetworks.HiddenLayer import HiddenLayer


class MutliLayerPerceptrons:
    u"""
    Class for MutliLayerPerceptrons
    """

    def __init__(self, dim_input_signal, dim_hidden, dim_output_signal, rand_obj):

        self.dim_input_signal = dim_input_signal
        self.dim_hidden = dim_hidden
        self.dim_output_signal = dim_output_signal

        if rand_obj is None:
            rand_obj = random(1234)

        self.rand_obj = rand_obj

        # construct hidden layer with tanh as activation function
        self.hidden_layer = HiddenLayer(dim_input_signal, dim_hidden, None, None, rand_obj, "Tanh")

        # construct output layer i.e. multi-class logistic layer
        self.logisticLayer = LogisticRegression(dim_hidden, dim_output_signal)

    def train(self, input_signals, teacher_labels, min_batch_size, learning_rate):

        hidden_output = [[0] * min_batch_size for i in range(min_batch_size)]
        y_err_arr = [[0] * self.dim_output_signal for i in range(min_batch_size)]

        # forward hidden layer
        for i in range(min_batch_size):
            hidden_output[i] = self.hidden_layer.foward(input_signals[i])

        # forward & backward output layer
        # delta = y - t ... (2.5.32)
        y_err_arr = self.logisticLayer.train(hidden_output, teacher_labels, min_batch_size, learning_rate)

        # backward hidden layer (backpropagate)
        self.hidden_layer.backward(input_signals, hidden_output, y_err_arr, self.logisticLayer.weights,
                                   min_batch_size, learning_rate)

    def predict(self, input_signals):
        # a_j = Sum{ w^T * x + b } ... (2.5.25)
        # z_j = h(a_j) ... (2.5.26)
        hidden_outputs = self.hidden_layer.output(input_signals)
        # a = Sum{ w^T * x + b } where a if from sigma(a) = sigma(w^T * x + b) ... (2.5.9)
        # y_k = exp(a_k) / Sum{ exp(a_k) } = exp(w_k^T * x + b_k) / Sum{ exp(w_k^T * x + b_k) } ... (2.5.18)
        # convert to binary label [0 of 1]
        return self.logisticLayer.predict(hidden_outputs)


if __name__ == '__main__':
    CNT_PATTERN         = 2
    CNT_TRAIN_DATA      = 4               # number of training data
    CNT_TEST_DATA       = 4               # number of test data
    DIM_INPUT_SIGNAL    = 2               # dimensions of input data
    DIM_HIDDEN          = 3               # dimensions of hidden
    DIM_OUTPUT_SIGNAL   = CNT_PATTERN     # dimensions of output data

    # input data for training
    train_input_data_set = [[0] * DIM_INPUT_SIGNAL for j in range(CNT_TRAIN_DATA)]
    # output data (label) for training
    train_teacher_labels = [0] * CNT_TRAIN_DATA

    # input data for test
    test_input_data_set = [[0] * DIM_INPUT_SIGNAL for j in range(CNT_TEST_DATA)]
    # label for inputs
    test_teacher_labels = [0] * CNT_TEST_DATA
    # output data predicted by the model
    test_predict_output_labels = [0] * CNT_TEST_DATA

    EPOCHS = 5000   # maximum training epochs
    learning_rate = 0.1  # learning rate

    MIN_BATCH_SIZE = 1  # here, we do on-line training
    CNT_MIN_BATCH = int(CNT_TRAIN_DATA / MIN_BATCH_SIZE)

    train_input_data_set_min_batch = [[[0] * DIM_INPUT_SIGNAL for j in range(MIN_BATCH_SIZE)]
                                      for k in range(CNT_MIN_BATCH)]
    train_teacher_data_set_min_batch = [[[0] * DIM_OUTPUT_SIGNAL for j in range(MIN_BATCH_SIZE)]
                                        for k in range(CNT_MIN_BATCH)]
    min_batch_indexes = list(range(CNT_TRAIN_DATA))
    random.shuffle(min_batch_indexes)   # shuffle data index for SGD

    #
    # Training simple XOR problem for demo
    #   class 1 : [0, 0], [1, 1]  ->  Negative [0, 1]
    #   class 2 : [0, 1], [1, 0]  ->  Positive [1, 0]
    #

    train_input_data_set = [[0., 0.], [0., 1.], [1., 0.], [1., 1.]]
    train_teacher_labels = [[0, 1], [1, 0], [1, 0], [0, 1]]
    test_input_data_set = [[0., 0.], [0., 1.], [1., 0.], [1., 1.]]
    test_teacher_labels = [[0, 1], [1, 0], [1, 0], [0, 1]]

    rand_obj = random.Random()
    rand_obj.seed(1234)

    # create minbatches with training data
    for i in range(CNT_MIN_BATCH):
        for j in range(MIN_BATCH_SIZE):
            idx = min_batch_indexes[i * MIN_BATCH_SIZE + j]
            train_input_data_set_min_batch[i][j] = train_input_data_set[idx]
            train_teacher_data_set_min_batch[i][j] = train_teacher_labels[idx]

    #
    # Build Multi-Layer Perceptrons model
    #

    # construct
    classifier = MutliLayerPerceptrons(DIM_INPUT_SIGNAL, DIM_HIDDEN, DIM_OUTPUT_SIGNAL, rand_obj)

    # train
    for epoch in range(EPOCHS):   # training epochs
        for (train_input_data_min_batch, train_teacher_data_min_batch) in \
                zip(train_input_data_set_min_batch, train_teacher_data_set_min_batch):
            classifier.train(train_input_data_min_batch, train_teacher_data_min_batch, MIN_BATCH_SIZE, learning_rate)

        if (epoch + 1) % 500 == 0:
            print('epoch ' + str(epoch + 1) +  ' out of ' + str(EPOCHS))

    # test
    for i, test_input_data in enumerate(test_input_data_set):
        test_predict_output_labels[i] = classifier.predict(test_input_data)

    #
    # Evaluate the model
    #
    confusion_matrix = [[0] * CNT_PATTERN for j in range(CNT_PATTERN)]
    accuracy = 0.
    precision = [0] * CNT_PATTERN
    recall = [0] * CNT_PATTERN

    for test_predict_output_label, test_teacher_labels in zip(test_predict_output_labels, test_teacher_labels):
        predicted_idx = test_predict_output_label.index(1)
        actual_idx = test_teacher_labels.index(1)

        confusion_matrix[actual_idx][predicted_idx] += 1

    for i in range(CNT_PATTERN):
        col = 0.
        row = 0.

        for j in range(CNT_PATTERN):
            if i == j:
                accuracy += confusion_matrix[i][j]
                precision[i] += confusion_matrix[j][i]
                recall[i] += confusion_matrix[i][j]

            col += confusion_matrix[j][i]
            row += confusion_matrix[i][j]

        precision[i] /= col
        recall[i] /= row

    accuracy /= CNT_TEST_DATA

    print('--------------------')
    print('MLP model evaluation')
    print('--------------------')
    print('Accuracy:  %.1f %%' % (accuracy * 100))
    print('Precision:')
    for i, precision_elem in enumerate(precision):
        print('class %d: %.1f %%' % (i+1, precision_elem * 100))
    print('Recall:')
    for i, recall_elem in enumerate(recall):
        print('class %d: %.1f %%' % (i+1, recall_elem * 100))

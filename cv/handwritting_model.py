import os
from tensorflow.keras.utils import to_categorical
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Conv2D
from tensorflow.keras.layers import MaxPooling2D
from tensorflow.keras.layers import Dense
from tensorflow.keras.layers import Flatten
from tensorflow.keras.optimizers import SGD
import tensorflow as tf

import numpy as np # linear algebra
import pandas as pd


#load the test set from kaggle (needs to be in your kaggle input directory)
testing_letter = pd.read_csv('/kaggle/input/emnist/emnist-letters-test.csv')
training_letter = pd.read_csv('/kaggle/input/emnist/emnist-letters-train.csv')

#establish training labels and images
y1 = np.array(training_letter.iloc[:,0].values)
x1 = np.array(training_letter.iloc[:,1:].values)
x1 = x1.reshape((x1.shape[0], 28, 28, 1))

#establish validation labels and images
y2 = np.array(testing_letter.iloc[:,0].values)
x2 = np.array(testing_letter.iloc[:,1:].values)
x2 = x2.reshape((x2.shape[0], 28, 28, 1))

#reshape the images into vectors so they can be input to the neural network
num_points_train= x1.shape[0]
train_images_size = train_images_height*train_images_width
train_images = train_images.reshape(num_points_train, 28, 28, 1)
num_points_val = x2.shape[0]
test_images_size = 28*28
test_images = test_images.reshape(num_points_val, 28,28, 1)
number_of_classes = 27

# change labels to categories 0-(up to and not including) 37
y1 = tf.keras.utils.to_categorical(y1, number_of_classes)
y2 = tf.keras.utils.to_categorical(y2, number_of_classes)

 

def prep_pixels(train, test):

    train_norm = train.astype('float32')
    test_norm = test.astype('float32')
    # normalize 
    train_norm = train_norm / 255.0
    test_norm = test_norm / 255.0

    return train_norm, test_norm
 
# define cnn model
def define_model():

	#defining the parameters of a neural network with 3 convolution layers and 2 dense layers
	#the dense layers are the actual parameter producing portion of the network
    model = Sequential()
    model.add(Conv2D(32, (3, 3), activation='relu', kernel_initializer='he_uniform', input_shape=(28, 28, 1)))
    model.add(MaxPooling2D((2, 2)))
    model.add(Conv2D(64, (3, 3), activation='relu', kernel_initializer='he_uniform'))
    model.add(Conv2D(64, (3, 3), activation='relu', kernel_initializer='he_uniform'))
    model.add(MaxPooling2D((2, 2)))
    model.add(Flatten())
    model.add(Dense(100, activation='relu', kernel_initializer='he_uniform'))
    model.add(Dense(27, activation='softmax'))
    # compile model

    #optimize model during every epoch with stochastic (essentially random direction) gradient 
    #descent by minimizing the cross entropy loss
    opt = SGD(learning_rate=0.01, momentum=0.9)
    model.compile(optimizer=opt, loss='categorical_crossentropy', metrics=['accuracy'])
    return model
 

def train():

    #load data
    trainX, trainY, testX, testY = x1,y1,x2,y2
    # process data
    trainX, testX = prep_pixels(trainX, testX)
    # define model
    model = define_model()
    # fit model
    model.fit(trainX, trainY, epochs=10, batch_size=32, verbose=0)
    # save model
    model.save("letter_model.h5")
 
# entry point, run the test harness
train()
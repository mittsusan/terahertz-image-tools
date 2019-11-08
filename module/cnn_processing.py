import os
import keras.backend.tensorflow_backend as KTF
import tensorflow as tf
import keras
from keras.models import Sequential, model_from_json
from keras.layers.convolutional import Conv2D, MaxPooling2D
from keras.layers.core import Dense, Dropout, Activation, Flatten
import matplotlib.pyplot as plt

class CNN:
    def __init__(self,classnum,traindir,image_color,im_size_width,im_size_height,flip):
        self.conv1 = 30
        self.conv2 = 20
        self.conv3 = 10
        self.dense1 = 100
        self.dense2 = classnum
        self.nb_epoch = 100
        self.nb_batch = 64
        self.learning_rate = 1e-3
        self.classnum = classnum
        self.traindir = traindir
        self.image_color = image_color
        self.im_size_width = im_size_width
        self.im_size_height = im_size_height
        self.flip = flip
        self.model_structure = 'convreluMax' + str(self.conv1) + '_convreluMax' + str(self.conv2) + '_convreluMax' + str(
            self.conv3) + '_dense' + str(self.dense1) + 'relu_softmax'
        self.f_log = self.traindir + self.image_color + 'width' + str(
            self.im_size_width) + 'height' + str(self.im_size_height) + 'flip' + str(
            self.flip) + '/' + self.model_structure + '_lr' + str(self.learning_rate) + '/Adam_epoch' + str(
            self.nb_epoch) + '_batch' + str(self.nb_batch)
        self.f_model = self.traindir + image_color + 'width' + str(
            im_size_width) + 'height' + str(self.im_size_height) + 'flip' + str(
            self.flip) + '/' + self.model_structure + '_lr' + str(self.learning_rate) + '/Adam_epoch' + str(
            self.nb_epoch) + '_batch' + str(self.nb_batch)
        os.makedirs(self.f_model, exist_ok=True)
        os.makedirs(self.f_log, exist_ok=True)

    def cnn_train(self,X_train,Y_train,X_test,Y_test):
        conv1 = self.conv1
        conv2 = self.conv2
        conv3 = self.conv3
        dense1 = self.dense1
        dense2 = self.dense2
        # ニュートラルネットワークで使用するモデル作成
        old_session = KTF.get_session()
        #old_session = tf.compat.v1.keras.backend.get_session()
        with tf.Graph().as_default():
            session = tf.Session('')
            KTF.set_session(session)
            KTF.set_learning_phase(1)

            model = Sequential()

            model.add(Conv2D(conv1, kernel_size=(3, 3), activation='relu', input_shape=(X_train.shape[1:])))
            model.add(MaxPooling2D(pool_size=(2, 2)))
            model.add(Conv2D(conv2, (3, 3), activation='relu'))
            model.add(MaxPooling2D(pool_size=(2, 2)))
            model.add(Conv2D(conv3, (3, 3), activation='relu'))
            # model.add(Dropout(0.25))
            # model.add(Conv2D(128, (3, 3), padding='same',activation='relu'))
            # model.add(MaxPooling2D(pool_size=(2, 2)))
            # model.add(Dropout(0.25))
            model.add(Flatten())
            model.add(Dense(dense1, activation='relu'))
            # model.add(Dropout(0.5))
            model.add(Dense(self.classnum, activation='softmax'))
            model.summary()
            # optimizer には adam を指定
            adam = keras.optimizers.Adam(lr=self.learning_rate)

            model.compile(loss='categorical_crossentropy', optimizer='adam', metrics=['accuracy'])
            # model.compile(loss='sparse_categorical_crossentropy',optimizer='adam',metrics=['accuracy'])
            es_cb = keras.callbacks.EarlyStopping(monitor='val_loss', min_delta=0, patience=100, verbose=0,
                                                  mode='auto')
            tb_cb = keras.callbacks.TensorBoard(log_dir=self.f_log, histogram_freq=1)
            # cp_cb = keras.callbacks.ModelCheckpoint(filepath = os.path.join(f_model,'cnn_model{epoch:02d}-loss{loss:.2f}-acc{acc:.2f}-vloss{val_loss:.2f}-vacc{val_acc:.2f}.hdf5'), monitor='val_loss', verbose=1, save_best_only=True, mode='auto')
            # cbks = [es_cb, tb_cb, cp_cb]
            cbks = [es_cb, tb_cb]
            # cbks = [tb_cb]
            history = model.fit(X_train, Y_train, batch_size=self.nb_batch, epochs=self.nb_epoch,
                                validation_data=(X_test, Y_test), callbacks=cbks, verbose=1)
            score = model.evaluate(X_test, Y_test, verbose=0)
            print('Test score:', score[0])
            print('Test accuracy:', score[1])
            print('save the architecture of a model')
            json_string = model.to_json()
            open(os.path.join(self.f_model, 'cnn_model.json'), 'w').write(json_string)
            yaml_string = model.to_yaml()
            open(os.path.join(self.f_model, 'cnn_model.yaml'), 'w').write(yaml_string)
            print('save weights')
            model.save_weights(os.path.join(self.f_model, 'cnn_weights.hdf5'))
        KTF.set_session(old_session)
        plt.plot(history.history['acc'])
        plt.plot(history.history['val_acc'])
        plt.title('model accuracy')
        plt.xlabel('epoch')
        plt.ylabel('accuracy')
        plt.legend(['acc', 'val_acc'], loc='lower right')
        plt.show()

        plt.plot(history.history['loss'])
        plt.plot(history.history['val_loss'])
        plt.title('model loss')
        plt.xlabel('epoch')
        plt.ylabel('loss')
        plt.legend(['loss', 'val_loss'], loc='lower right')
        plt.show()
        return

    def cnn_test(self,video_file_name):
        # ニュートラルネットワークで使用するモデル作成
        model_filename = 'cnn_model.json'
        weights_filename = 'cnn_weights.hdf5'
        old_session = KTF.get_session()
        with tf.Graph().as_default():
            session = tf.Session('')
            KTF.set_session(session)

            json_string = open(os.path.join(self.f_model, model_filename)).read()
            model = model_from_json(json_string)

            model.summary()
            adam = keras.optimizers.Adam(lr=self.learning_rate)
            model.compile(loss='categorical_crossentropy', optimizer='adam', metrics=['accuracy'])

            model.load_weights(os.path.join(self.f_model, weights_filename))

            cbks = []
            video_predict(video_file_name)

        KTF.set_session(old_session)
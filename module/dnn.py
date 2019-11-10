import os
import numpy as np
from keras.utils import np_utils
import matplotlib.pyplot as plt
import glob
import cv2
from module.cnn_processing import CNN


class DNNClasifier:
    def __init__(self,imtype,traindir,valdir,classnum):
        self.imtype = imtype
        self.traindir = traindir
        self.valdir = valdir
        self.classnum = classnum
        if self.imtype == 'image':
            self.image_color = 'RGB'
            self.im_size_width = 30
            self.im_size_height = 44
            self.flip = 1  # 1の場合画像を左右反転,0の場合、上下反転、-1の場合上下左右反転、Noneでなし。
    def train(self):
        def load_pic(data_path):
            # ファイルのパスの読み込み
            path_list = glob.glob(data_path + '/*')
            # 画像読み込み用のリストの用意
            file_list = []
            # 画像の読み込み
            for i in path_list:
                def recursive_file_check(i):
                    if os.path.isdir(i):
                        # ディレクトリの中身を見る
                        files = os.listdir(i)
                        for file in files:
                            recursive_file_check(i + "/" + file)
                    else:
                        basename, ext = os.path.splitext(i)
                        if ext == '.jpg' or ext == '.png' or ext == '.jpeg':
                            print('処理予定{}'.format(i))
                            image = cv2.imread(i)
                            # bgrからrgbへの変換(openCVでは一般的にBGR)
                            if self.image_color == 'RGB':
                                image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
                            elif self.image_color == 'GRAY':
                                image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
                            image = cv2.resize(image, (self.im_size_width, self.im_size_height))  # サイズ変更して圧縮
                            if self.flip == None:
                                pass
                            elif self.flip == 0:
                                image = cv2.flip(image, 0)  # 画像を上下反転
                            elif self.flip == 1:
                                image = cv2.flip(image, 1)  # 画像を左右反転
                            elif self.flip == -1:
                                image = cv2.flip(image, -1)  # 画像を上下左右反転
                            file_list.append(image)
                        elif ext == '.txt':
                            print('処理予定{}'.format(i))
                            ##注意
                            beam_ave = np.loadtxt(i)
                            file_list.append(beam_ave)

                recursive_file_check(i)
            file_np = np.array(file_list)
            # print(file_np.shape)
            return file_np
        def label_append(data_path):
            y_all = []
            flag = 0
            number = 0
            file_list = sorted(glob.glob(data_path + '/*'))
            print('読み込みクラスリスト数(予定){}'.format(len(file_list)))
            print(file_list)
            for j in file_list:
                try:
                    if '.npy' not in j:
                        print('loading:{}'.format(j))
                        x = load_pic(j)
                        if flag == 0:
                            x_all = x
                            flag += 1
                            # print(x_all)
                        else:
                            x_all = np.append(x_all, x, axis=0)

                        for k in range(x.shape[0]):
                            y_all.append(number)  # ラベル付け

                            # print(y_all)
                        number = number + 1
                except FileNotFoundError as e:
                    print(e)
            return (x_all, y_all)

        if self.imtype == 'image':
            npy_train_data_dir = self.traindir  + self.image_color + 'width' + str(
                self.im_size_width) + 'height' + str(self.im_size_height) + 'flip' + str(self.flip)
            npy_val_data_dir = self.valdir  + self.image_color + 'width' + str(
                self.im_size_width) + 'height' + str(self.im_size_height) + 'flip' + str(self.flip)
        else:
            npy_train_data_dir = self.traindir  + self.imtype
            npy_val_data_dir = self.valdir  + self.imtype

        train_data_Xnpy = npy_train_data_dir + 'X.npy'
        train_data_Ynpy = npy_train_data_dir + 'Y.npy'
        val_data_Xnpy = npy_val_data_dir + 'X.npy'
        val_data_Ynpy = npy_val_data_dir + 'Y.npy'

        if os.path.exists(train_data_Xnpy):
            pass
            print('pass')
        else:
            print('pass出来ていない')
            (x_all_1, y_all_1) = label_append(self.traindir)
            (x_all_2, y_all_2) = label_append(self.valdir)
            # 画素値を0から1の範囲に変換
            X_1 = x_all_1.astype('float32')
            X_train = X_1 / 255.0

            X_2 = x_all_2.astype('float32')
            X_test = X_2 / 255.0

            # クラスの形式を変換
            Y_train = np_utils.to_categorical(np.array(y_all_1), self.classnum)
            Y_test = np_utils.to_categorical(np.array(y_all_2), self.classnum)

            # print(X_train)
            print(len(X_train))
            # print(Y_train)
            print(len(Y_train))
            print(len(X_test))
            print(len(Y_test))

        ##npyデータファイル読み込みor保存
        if os.path.exists(train_data_Xnpy):
            X_train = np.load(train_data_Xnpy)

        else:
            np.save(npy_train_data_dir + 'X', X_train)

        if os.path.exists(train_data_Ynpy):
            Y_train = np.load(train_data_Ynpy)

        else:
            np.save(npy_train_data_dir + 'Y', Y_train)

        if os.path.exists(val_data_Xnpy):
            X_test = np.load(val_data_Xnpy)

        else:
            np.save(npy_val_data_dir + 'X', X_test)

        if os.path.exists(val_data_Ynpy):
            Y_test = np.load(val_data_Ynpy)

        else:
            np.save(npy_val_data_dir + 'Y', Y_test)

        print(X_train.shape)
        print(X_test.shape)
        if self.imtype == 'image':
            if self.image_color == 'GRAY':
                X_train.resize(X_train.shape[0], X_train.shape[1], X_train.shape[2], 1)
                X_test.resize(X_test.shape[0], X_test.shape[1], X_test.shape[2], 1)

            elif self.image_color == 'RGB':
                pass

            CNN(self.classnum,self.traindir,self.image_color,self.im_size_width,self.im_size_height,self.flip).cnn_train(X_train,Y_train,X_test,Y_test)

        else:
            print(X_train.shape[1:])
            # print(type(X_test))
            # print(Y_train)
            # print(type(Y_test))

    def test(self,trigger_type,gain,exp,classnamelist):
        CNN(self.classnum, self.traindir, self.image_color, self.im_size_width, self.im_size_height,
            self.flip).cnn_test(trigger_type,gain,exp,classnamelist)
        return
import os
import numpy as np
from keras.utils import np_utils
#import matplotlib.pyplot as plt
import glob
import cv2
from module.cnn_processing import CNN
from module.imread_imwrite_japanese import ImreadImwriteJapanese


class DNNClasifier:
    def __init__(self, traindir, valdir, flip, epoch):
        self.sampledir = os.path.dirname(traindir)
        self.traindir = traindir
        self.valdir = valdir
        self.im_size_width = 30
        self.im_size_height = 44
        self.epoch = epoch
        self.flip = flip
        self.im_jp = ImreadImwriteJapanese
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
                            #image = cv2.imread(i,cv2.IMREAD_GRAYSCALE)
                            image = self.im_jp.imread(i,cv2.IMREAD_GRAYSCALE)
                            image = cv2.resize(image, (self.im_size_width, self.im_size_height))  # サイズ変更して圧縮
                            '''
                            if self.flip == 'normal':
                                pass
                            elif self.flip == 'flip':
                                image = cv2.flip(image, 1)  # 画像を左右反転
                            '''
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

            return x_all, y_all, file_list



        npy_train_data_dir = self.traindir  + 'width' + str(
            self.im_size_width) + 'height' + str(self.im_size_height) + 'flip' + self.flip

        if len(self.valdir) == 0:
            pass
        else:
            npy_val_data_dir = self.valdir  + 'width' + str(
                self.im_size_width) + 'height' + str(self.im_size_height) + 'flip' + self.flip


        #サンプル配下ディレクトリに入る
        train_data_Xnpy = npy_train_data_dir + 'X.npy'
        train_data_Ynpy = npy_train_data_dir + 'Y.npy'
        if len(self.valdir) == 0:
            pass
        else:
            val_data_Xnpy = npy_val_data_dir + 'X.npy'
            val_data_Ynpy = npy_val_data_dir + 'Y.npy'

        ##npyデータファイル読み込みor保存
        if os.path.exists(train_data_Xnpy) and os.path.exists(train_data_Ynpy):
            print('npyデータ存在')
            X_train = np.load(train_data_Xnpy)
            Y_train = np.load(train_data_Ynpy)
            if len(self.valdir) == 0:
                pass
            else:
                X_test = np.load(val_data_Xnpy)
                Y_test = np.load(val_data_Ynpy)

            # class名読み込み
            with open(os.path.join(self.sampledir,'classname.txt')) as f:
                class_list = [s.strip() for s in f.readlines()]
                print(class_list)

        else:
            print('データ読み込み')
            x_all_1, y_all_1, class_list = label_append(self.traindir)
            if len(self.valdir) == 0:
                pass
            else:
                x_all_2, y_all_2, class_list = label_append(self.valdir)
            # 画素値を0から1の範囲に変換
            X_1 = x_all_1.astype('float32')
            X_train = X_1 / 255.0
            Y_train = np_utils.to_categorical(np.array(y_all_1), len(class_list))
            if len(self.valdir) == 0:
                pass
            else:
                X_2 = x_all_2.astype('float32')
                X_test = X_2 / 255.0
                Y_test = np_utils.to_categorical(np.array(y_all_2), len(class_list))


            #クラス名保存
            with open(os.path.join(self.sampledir,'classname.txt'), 'wt') as f:
                for ele in class_list:
                    basename = os.path.basename(ele)
                    root, ext = os.path.splitext(basename)
                    f.write(root + '\n')

            # npy保存
            np.save(npy_train_data_dir + 'X', X_train)
            np.save(npy_train_data_dir + 'Y', Y_train)
            if len(self.valdir) == 0:
                pass
            else:
                np.save(npy_val_data_dir + 'X', X_test)
                np.save(npy_val_data_dir + 'Y', Y_test)

        X_train.resize(X_train.shape[0], X_train.shape[1], X_train.shape[2], 1)
        if len(self.valdir) == 0:
            CNN(len(class_list), self.traindir, self.im_size_width, self.im_size_height,
                self.flip, self.epoch).cnn_train_noneval(X_train, Y_train)
        else:
            X_test.resize(X_test.shape[0], X_test.shape[1], X_test.shape[2], 1)
            CNN(len(class_list), self.traindir, self.im_size_width, self.im_size_height,
            self.flip, self.epoch).cnn_train(X_train, Y_train, X_test, Y_test)


    def test(self, trigger_type, gain, exp, cvv):
        # class名読み込み
        with open(os.path.join(self.sampledir, 'classname.txt')) as f:
            class_list = [s.strip() for s in f.readlines()]
        CNN(len(class_list), self.traindir, self.im_size_width, self.im_size_height,
            self.flip, self.epoch).cnn_test(trigger_type, gain, exp, class_list, cvv)

    def test_color(self, trigger_type, gain, exp, cvv):
        # class名読み込み
        with open(os.path.join(self.sampledir, 'classname.txt')) as f:
            class_list = [s.strip() for s in f.readlines()]
        CNN(len(class_list), self.traindir, self.im_size_width, self.im_size_height,
            self.flip, self.epoch).cnn_test_color(trigger_type, gain, exp, class_list, cvv)
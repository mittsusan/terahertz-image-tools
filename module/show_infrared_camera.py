from module.camera_manager import CameraManager
from module.camera_manager import TriggerType
from module.camera_manager import AcquisitionMode
from module.camera_manager import AutoExposureMode
from module.camera_manager import AutoGainMode
import cv2
import time
import numpy as np

class ShowInfraredCamera():
    def __init__(self):
        self.cam_manager = CameraManager()
        self.savecount = 0
        self.colormap_table_count = 0
        self.colormap_table = [
            ['COLORMAP_AUTUMN', cv2.COLORMAP_AUTUMN],
            ['COLORMAP_JET', cv2.COLORMAP_JET],
            ['COLORMAP_WINTER', cv2.COLORMAP_WINTER],
            ['COLORMAP_RAINBOW', cv2.COLORMAP_RAINBOW],
            ['COLORMAP_OCEAN', cv2.COLORMAP_OCEAN],
            ['COLORMAP_SUMMER', cv2.COLORMAP_SUMMER],
            ['COLORMAP_SPRING', cv2.COLORMAP_SPRING],
            ['COLORMAP_COOL', cv2.COLORMAP_COOL],
            ['COLORMAP_HSV', cv2.COLORMAP_HSV],
            ['COLORMAP_PINK', cv2.COLORMAP_PINK],
            ['COLORMAP_HOT', cv2.COLORMAP_HOT]
        ]

    def show_beam(self, trigger, gain, exp):

        if trigger == "software":
            self.cam_manager.choose_trigger_type(TriggerType.SOFTWARE)
        elif trigger == "hardware":
            self.cam_manager.choose_trigger_type(TriggerType.HARDWARE)

        self.cam_manager.turn_on_trigger_mode()

        self.cam_manager.choose_acquisition_mode(AcquisitionMode.CONTINUOUS)

        self.cam_manager.choose_auto_exposure_mode(AutoExposureMode.OFF)
        self.cam_manager.set_exposure_time(exp)

        self.cam_manager.choose_auto_gain_mode(AutoGainMode.OFF)
        self.cam_manager.set_gain(gain)

        self.cam_manager.start_acquisition()

        while True:
            # 処理前の時刻
            t1 = time.time()
            if trigger == "software":
                self.cam_manager.execute_software_trigger()

            frame = self.cam_manager.get_next_image()
            if frame is None:
                continue

            cv2.imshow("Please push Q button when you want to close the window.",
                       cv2.resize(frame, (1024, 1024)))

            if self.savecount != 0:
                cv2.imwrite(self.savepath + '/{}.png'.format(self.savecount), frame)
                self.savecount += -1
                print('saveimage:{}'.format(self.savecount))

            if cv2.waitKey(1) & 0xFF == ord('q'):
                cv2.destroyAllWindows()
                print('Complete Cancel')
                break

            # 処理後の時刻
            t2 = time.time()

            # 経過時間を表示
            freq = 1 / (t2 - t1)
            print(f"フレームレート：{freq}fps")

        self.cam_manager.stop_acquisition()

    def show_beam_color(self,trigger,gain,exp):

        if trigger == "software":
            self.cam_manager.choose_trigger_type(TriggerType.SOFTWARE)
        elif trigger == "hardware":
            self.cam_manager.choose_trigger_type(TriggerType.HARDWARE)

        self.cam_manager.turn_on_trigger_mode()

        self.cam_manager.choose_acquisition_mode(AcquisitionMode.CONTINUOUS)

        self.cam_manager.choose_auto_exposure_mode(AutoExposureMode.OFF)
        self.cam_manager.set_exposure_time(exp)

        self.cam_manager.choose_auto_gain_mode(AutoGainMode.OFF)
        self.cam_manager.set_gain(gain)

        self.cam_manager.start_acquisition()

        while True:
            # 処理前の時刻
            t1 = time.time()
            if trigger == "software":
                self.cam_manager.execute_software_trigger()

            frame = self.cam_manager.get_next_image()
            if frame is None:
                continue

            # 疑似カラーを付与
            apply_color_map_image = cv2.applyColorMap(frame,
                                                      self.colormap_table[self.colormap_table_count % len(self.colormap_table)][1])

            cv2.putText(apply_color_map_image, self.colormap_table[self.colormap_table_count % len(self.colormap_table)][0],
                        (20, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.75, (0, 0, 0), 2)

            cv2.imshow("Please push Q button when you want to close the window.",
                       cv2.resize(apply_color_map_image, (1024, 1024)))



            if self.savecount != 0:
                cv2.imwrite(self.savepath + '/{}.png'.format(self.savecount), frame)
                self.savecount += -1
                print('saveimage:{}'.format(self.savecount))

            if cv2.waitKey(1) & 0xff == 110:  # N
                self.colormap_table_count = self.colormap_table_count + 1

            if cv2.waitKey(1) & 0xFF == ord('q'):
                cv2.destroyAllWindows()
                print('Complete Cancel')
                break

            # 処理後の時刻
            t2 = time.time()

            # 経過時間を表示
            freq = 1 / (t2 - t1)
            print(f"フレームレート：{freq}fps")

        self.cam_manager.stop_acquisition()

    def realtime_identification(self, classnamelist, model, trigger, gain, exp, im_size_width, im_size_height, flip):

        if trigger == "software":
            self.cam_manager.choose_trigger_type(TriggerType.SOFTWARE)
        elif trigger == "hardware":
            self.cam_manager.choose_trigger_type(TriggerType.HARDWARE)

        self.cam_manager.turn_on_trigger_mode()

        self.cam_manager.choose_acquisition_mode(AcquisitionMode.CONTINUOUS)

        self.cam_manager.choose_auto_exposure_mode(AutoExposureMode.OFF)
        self.cam_manager.set_exposure_time(exp)

        self.cam_manager.choose_auto_gain_mode(AutoGainMode.OFF)
        self.cam_manager.set_gain(gain)

        self.cam_manager.start_acquisition()

        font = cv2.FONT_HERSHEY_PLAIN
        fontsize = 8
        samplename_position_x = 360
        samplename_position_y = 120
        probability_position_x = 360
        probability_position_y = 220
        x_move = 1100
        font_scale = 6
        while True:
            # 処理前の時刻
            t1 = time.time()
            if trigger == "software":
                self.cam_manager.execute_software_trigger()

            frame = self.cam_manager.get_next_image()
            if frame is None:
                continue
            # 読み込んだフレームを書き込み

            if flip == None:
                pass
            elif flip == 0:
                frame = cv2.flip(frame, 0)  # 画像を上下反転
            elif flip == 1:
                frame = cv2.flip(frame, 1)  # 画像を左右反転
            elif flip == -1:
                frame = cv2.flip(frame, -1)  # 画像を上下左右反転

            resize_image = cv2.resize(frame, (im_size_width, im_size_height))
            # print(resize_image)
            # print('writing')
            X = []
            X.append(resize_image)
            X = np.array(X)
            X = X.astype("float") / 256

            X.resize(X.shape[0], X.shape[1], X.shape[2], 1)

            predict = model.predict(X)

            for (i, pre) in enumerate(predict):
                y = pre.argmax()  # preがそれぞれの予測確率で一番高いものを取ってきている。Y_testはone-hotベクトル

                cv2.putText(frame, 'Predict sample', (samplename_position_x, samplename_position_y), font, fontsize,
                            (255, 255, 255), font_scale, cv2.LINE_AA)
                cv2.putText(frame, 'Probability', (probability_position_x, probability_position_y), font, fontsize,
                            (255, 255, 255), font_scale, cv2.LINE_AA)
                pretext = classnamelist[y]
                cv2.putText(frame, pretext, (samplename_position_x + x_move, samplename_position_y), font, fontsize,
                            (255, 255, 255), font_scale, cv2.LINE_AA)

                print("予測: {0}  {1}% ".format(y, round(pre[y] * 100)))

                if pre[y] > 0.9:  # 確率が90%を超える時
                    cv2.putText(frame, '{}%'.format(round(pre[y] * 100)),
                                (probability_position_x + x_move, probability_position_x), font, fontsize,
                                (0, 0, 255), font_scale, cv2.LINE_AA)
                else:
                    cv2.putText(frame, '{}%'.format(round(pre[y] * 100)),
                                (probability_position_x + x_move, probability_position_y), font, fontsize,
                                (255, 255, 255), font_scale, cv2.LINE_AA)

            cv2.imshow("Please push Q button when you want to close the window.",
                       cv2.resize(frame, (1024, 1024)))

            if self.savecount != 0:
                cv2.imwrite(self.savepath + '/{}.png'.format(self.savecount), frame)
                self.savecount += -1
                print('saveimage:{}'.format(self.savecount))

            if cv2.waitKey(1) & 0xFF == ord('q'):
                cv2.destroyAllWindows()
                print('Complete Cancel')
                break

            # 処理後の時刻
            t2 = time.time()

            # 経過時間を表示
            freq = 1 / (t2 - t1)
            print(f"フレームレート：{freq}fps")

        self.cam_manager.stop_acquisition()
        print('Stopped Camera')

    def realtime_identification_color(self,classnamelist,model,trigger,gain,exp,im_size_width,im_size_height,flip):

        if trigger == "software":
            self.cam_manager.choose_trigger_type(TriggerType.SOFTWARE)
        elif trigger == "hardware":
            self.cam_manager.choose_trigger_type(TriggerType.HARDWARE)

        self.cam_manager.turn_on_trigger_mode()

        self.cam_manager.choose_acquisition_mode(AcquisitionMode.CONTINUOUS)

        self.cam_manager.choose_auto_exposure_mode(AutoExposureMode.OFF)
        self.cam_manager.set_exposure_time(exp)

        self.cam_manager.choose_auto_gain_mode(AutoGainMode.OFF)
        self.cam_manager.set_gain(gain)

        self.cam_manager.start_acquisition()

        font = cv2.FONT_HERSHEY_PLAIN
        fontsize = 8
        samplename_position_x = 360
        samplename_position_y = 120
        probability_position_x = 360
        probability_position_y = 220
        x_move = 1100
        font_scale = 6
        while True:
            # 処理前の時刻
            t1 = time.time()
            if trigger == "software":
                self.cam_manager.execute_software_trigger()

            frame = self.cam_manager.get_next_image()
            if frame is None:
                continue
            # 読み込んだフレームを書き込み
            if flip == None:
                pass
            elif flip == 0:
                frame = cv2.flip(frame, 0)  # 画像を上下反転
            elif flip == 1:
                frame = cv2.flip(frame, 1)  # 画像を左右反転
            elif flip == -1:
                frame = cv2.flip(frame, -1)  # 画像を上下左右反転

            resize_image = cv2.resize(frame, (im_size_width, im_size_height))

            X = []
            X.append(resize_image)
            X = np.array(X)
            X = X.astype("float") / 256

            X.resize(X.shape[0], X.shape[1], X.shape[2], 1)

            predict = model.predict(X)

            for (i, pre) in enumerate(predict):
                y = pre.argmax()  # preがそれぞれの予測確率で一番高いものを取ってきている。Y_testはone-hotベクトル

                cv2.putText(frame, 'Predict sample', (samplename_position_x, samplename_position_y), font, fontsize, (255, 255, 255), font_scale, cv2.LINE_AA)
                cv2.putText(frame, 'Probability', (probability_position_x, probability_position_y), font, fontsize,
                            (255, 255, 255), font_scale, cv2.LINE_AA)
                pretext = classnamelist[y]
                cv2.putText(frame, pretext, (samplename_position_x+x_move,samplename_position_y), font, fontsize, (255, 255, 255), font_scale, cv2.LINE_AA)

                print("予測: {0}  {1}% ".format(y, round(pre[y] * 100)))

                if pre[y] > 0.9:  # 確率が90%を超える時
                    cv2.putText(frame, '{}%'.format(round(pre[y] * 100)), (probability_position_x+x_move, probability_position_x), font, fontsize,
                                (0, 0, 255), font_scale, cv2.LINE_AA)
                else:
                    cv2.putText(frame, '{}%'.format(round(pre[y] * 100)), (probability_position_x+x_move, probability_position_y), font, fontsize,
                                (255, 255, 255), font_scale, cv2.LINE_AA)
            # 疑似カラーを付与
            apply_color_map_image = cv2.applyColorMap(frame,self.colormap_table[self.colormap_table_count % len(self.colormap_table)][1])

            cv2.putText(apply_color_map_image,
                        self.colormap_table[self.colormap_table_count % len(self.colormap_table)][0],
                        (20, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.75, (0, 0, 0), 2)
            cv2.imshow("Please push Q button when you want to close the window.",
                       cv2.resize(apply_color_map_image, (1024, 1024)))


            if self.savecount != 0:
                cv2.imwrite(self.savepath + '/{}.png'.format(self.savecount), frame)
                self.savecount += -1
                print('saveimage:{}'.format(self.savecount))

            if cv2.waitKey(1) & 0xff == 110:  # N
                self.colormap_table_count = self.colormap_table_count + 1

            if cv2.waitKey(1) & 0xFF == ord('q'):
                cv2.destroyAllWindows()
                print('Complete Cancel')
                break

            # 処理後の時刻
            t2 = time.time()

            # 経過時間を表示
            freq = 1 / (t2 - t1)
            print(f"フレームレート：{freq}fps")

        self.cam_manager.stop_acquisition()
        print('Stopped Camera')
    def save(self,savecount, savepath):
        self.savecount = savecount
        self.savepath = savepath











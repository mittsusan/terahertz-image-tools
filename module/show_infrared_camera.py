from module.camera_manager import CameraManager
from module.camera_manager import TriggerType
from module.camera_manager import AcquisitionMode
from module.camera_manager import AutoExposureMode
from module.camera_manager import AutoGainMode
import cv2
import time

class ShowInfraredCamera():
    def __init__(self):
        self.cam_manager = CameraManager()
        self.savecount = 0
    def show_beam(self,trigger,gain,exp):

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

            img = self.cam_manager.get_next_image()
            if img is None:
                continue

            cv2.imshow("Please push Q button when you want to close the window.",
                       cv2.resize(img, (1024, 1024)))


            if self.savecount != 0:
                cv2.imwrite(self.savepath + '/{}.png'.format(self.savecount), self.cvv.frame)
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

    def save(self,savecount, savepath):
        self.savecount = savecount
        self.savepath = savepath











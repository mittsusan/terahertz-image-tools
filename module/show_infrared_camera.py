from module.camera_manager import CameraManager
from module.camera_manager import TriggerType
from module.camera_manager import AcquisitionMode
from module.camera_manager import AutoExposureMode
from module.camera_manager import AutoGainMode

class ShowInfraredCamera:
    def __init__(self):
        self.cam_manager = CameraManager()
    def configure(self,trigger,gain,exp):


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

    def cameraFrame(self,trigger,gain,exp):

        if trigger == "software":
            self.cam_manager.execute_software_trigger()

        self.frame = self.cam_manager.get_next_image()
        #self.frame = cv2.cvtColor(self.frame, cv2.COLOR_BGR2RGB)


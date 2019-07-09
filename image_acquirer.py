from camera_manager import CameraManager
from camera_manager import TriggerType
from camera_manager import AcquisitionMode
from camera_manager import AutoExposureMode
from camera_manager import AutoGainMode

import cv2

if __name__ == "__main__":
    cam_manager = CameraManager()

    cam_manager.choose_trigger_type(TriggerType.SOFTWARE)
    cam_manager.turn_on_trigger_mode()

    cam_manager.choose_acquisition_mode(AcquisitionMode.CONTINUOUS)

    cam_manager.choose_auto_exposure_mode(AutoExposureMode.OFF)
    cam_manager.set_exposure_time(20000)

    cam_manager.choose_auto_gain_mode(AutoGainMode.OFF)
    cam_manager.set_gain(0)

    cam_manager.start_acquisition()

    while True:
        cam_manager.execute_software_trigger()
        img = cam_manager.get_next_image()
        if img is None:
            continue

        img = cv2.resize(img, (1024, 1024))
        cv2.imshow("captured image", img)
        if 0 <= cv2.waitKey(5):
            break

    cam_manager.stop_acquisition()

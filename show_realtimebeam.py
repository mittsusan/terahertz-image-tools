from module.camera_manager import CameraManager
from module.camera_manager import TriggerType
from module.camera_manager import AcquisitionMode
from module.camera_manager import AutoExposureMode
from module.camera_manager import AutoGainMode

import argparse
from pathlib import Path
import time

import cv2

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("trigger", default="software", type=str, choices=["software", "hardware"], help="trigger type")
    parser.add_argument("--exp", default=20000, type=int, help="exposure time [us]")
    parser.add_argument("--gain", default=0, type=int, help="gain [dB]")

    args = parser.parse_args()


    cam_manager = CameraManager()

    if args.trigger == "software":
        cam_manager.choose_trigger_type(TriggerType.SOFTWARE)
    elif args.trigger == "hardware":
        cam_manager.choose_trigger_type(TriggerType.HARDWARE)

    cam_manager.turn_on_trigger_mode()

    cam_manager.choose_acquisition_mode(AcquisitionMode.CONTINUOUS)

    cam_manager.choose_auto_exposure_mode(AutoExposureMode.OFF)
    cam_manager.set_exposure_time(args.exp)

    cam_manager.choose_auto_gain_mode(AutoGainMode.OFF)
    cam_manager.set_gain(args.gain)

    cam_manager.start_acquisition()

    while True:
        # 処理前の時刻
        t1 = time.time()
        if args.trigger == "software":
            cam_manager.execute_software_trigger()

        img = cam_manager.get_next_image()
        if img is None:
            continue

        cv2.imshow("Showing image", cv2.resize(img, (1024, 1024)))

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

        # 処理後の時刻
        t2 = time.time()

        # 経過時間を表示
        freq = 1 / (t2 - t1)
        print(f"フレームレート：{freq}fps")
    cam_manager.stop_acquisition()

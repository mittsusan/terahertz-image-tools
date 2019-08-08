from module.camera_manager import CameraManager
from module.camera_manager import TriggerType
from module.camera_manager import AcquisitionMode
from module.camera_manager import AutoExposureMode
from module.camera_manager import AutoGainMode

import argparse
from pathlib import Path

import cv2

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("trigger", default="software", type=str, choices=["software", "hardware"], help="trigger type")
    parser.add_argument("--exp", default=20000, type=int, help="exposure time [us]")
    parser.add_argument("--gain", default=0, type=int, help="gain [dB]")
    parser.add_argument("--save-dir", default=None, type=Path, help="directory to save images")
    parser.add_argument("--num-imgs", default=100, type=int, help="number of images to save")
    args = parser.parse_args()

    if args.save_dir is not None:
        args.save_dir.mkdir(parents=True, exist_ok=False)

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

    count = 0
    while True:
        if args.trigger == "software":
            cam_manager.execute_software_trigger()

        img = cam_manager.get_next_image()
        if img is None:
            continue

        cv2.imshow("captured image", cv2.resize(img, (1024, 1024)))
        if args.save_dir is not None:
            cv2.imwrite(str(args.save_dir / "{:0>6}.png".format(count)), img)

        if 0 <= cv2.waitKey(3):
            break

        count += 1
        if args.save_dir is not None and args.num_imgs <= count:
            break

    cam_manager.stop_acquisition()

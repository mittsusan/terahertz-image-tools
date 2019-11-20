# -*- coding: utf-8 -*-
import PySpin


class TriggerType():
    SOFTWARE = "Software"
    HARDWARE = "Line0"


class AcquisitionMode():
    CONTINUOUS = "Continuous"
    SINGLE_FRAME = "SingleFrame"
    MULTI_FRAME = "MultiFrame"


class AutoExposureMode():
    ON = "On"
    OFF = "Off"


class AutoGainMode():
    ON = "On"
    OFF = "Off"


class CameraManager:
    def __init__(self, trigger_type=TriggerType.SOFTWARE):
        # カメラシステムを取得
        print("acquire the camera system")
        self.system = PySpin.System.GetInstance()

        # ライブラリのバージョンを表示
        version = self.system.GetLibraryVersion()
        print("PySpin library version: {}.{}.{}.{}".format(version.major, version.minor, version.type, version.build))

        # カメラリストを取得
        cam_list = self.system.GetCameras()
        # 1台しかカメラが接続されていないことを想定しているため，
        # 2台以上接続されていたら例外を投げる
        if cam_list.GetSize() != 1:
            raise RuntimeError("please connect the only ONE camera")
            self.__del__()
        self.cam = cam_list[0]
        self.print_camera_info()

        # カメラを初期化
        print("initialize the camera")
        self.cam.Init()

    def __del__(self):
        # カメラを解放
        print("destruct the camera")
        try:
            del self.cam
        except AttributeError:
            pass

        # カメラシステムを解放
        print("release the camera system")
        self.system.ReleaseInstance()

    def print_camera_info(self):
        print("========== Camera Information ==========")
        nodemap = self.cam.GetTLDeviceNodeMap()
        node_device_info = PySpin.CCategoryPtr(nodemap.GetNode("DeviceInformation"))
        if PySpin.IsAvailable(node_device_info) \
           and PySpin.IsReadable(node_device_info):
            features = node_device_info.GetFeatures()
            for feature in features:
                node_feature = PySpin.CValuePtr(feature)
                print("{}: {}".format(node_feature.GetName(),
                                      node_feature.ToString() if PySpin.IsReadable(node_feature) else "node not readable"))
        else:
            print("not available")
        print("========================================")

    def start_acquisition(self):
        self.cam.BeginAcquisition()

    def stop_acquisition(self):
        self.cam.EndAcquisition()

    def choose_trigger_type(self, trigger_type):
        print("trigger type: {}".format(trigger_type))

        # トリガーの設定を変更するため，トリガーモードを一時的にOFFにする
        is_trigger_mode_now = self.trigger_mode()
        if is_trigger_mode_now:
            self.turn_off_trigger_mode(False)

        nodemap = self.cam.GetNodeMap()

        node_trigger_source = PySpin.CEnumerationPtr(nodemap.GetNode("TriggerSource"))
        if not PySpin.IsAvailable(node_trigger_source) or not PySpin.IsWritable(node_trigger_source):
            raise RuntimeError("unable to get trigger source (node retrieval)")

        node_chosen_source = node_trigger_source.GetEntryByName(trigger_type)
        if not PySpin.IsAvailable(node_chosen_source) or not PySpin.IsReadable(node_chosen_source):
            raise RuntimeError("unable to set trigger source (enum entry retrieval)")
        node_trigger_source.SetIntValue(node_chosen_source.GetValue())

        trigger_activation_type = "RisingEdge"

        node_trigger_activation = PySpin.CEnumerationPtr(nodemap.GetNode("TriggerActivation"))
        if not PySpin.IsAvailable(node_trigger_activation) or not PySpin.IsWritable(node_trigger_activation):
            raise RuntimeError("unable to get trigger activation (node retrieval)")

        node_chosen_activation = node_trigger_activation.GetEntryByName(trigger_activation_type)
        if not PySpin.IsAvailable(node_chosen_activation) or not PySpin.IsReadable(node_chosen_activation):
            raise RuntimeError("unable to set trigger activation type (enum entry retrieval)")
        node_trigger_activation.SetIntValue(node_chosen_activation.GetValue())

        # トリガーモードを再開する
        if is_trigger_mode_now:
            self.turn_on_trigger_mode(False)

    def trigger_mode(self):
        nodemap = self.cam.GetNodeMap()

        node_trigger_mode = PySpin.CEnumerationPtr(nodemap.GetNode("TriggerMode"))
        if not PySpin.IsAvailable(node_trigger_mode) or not PySpin.IsReadable(node_trigger_mode):
            raise RuntimeError("unable to turn off trigger mode (node retrieval)")

        return bool(node_trigger_mode.GetIntValue())

    def turn_off_trigger_mode(self, stdout=True):
        if stdout:
            print("trigger mode: OFF")
        nodemap = self.cam.GetNodeMap()

        node_trigger_mode = PySpin.CEnumerationPtr(nodemap.GetNode("TriggerMode"))
        if not PySpin.IsAvailable(node_trigger_mode) or not PySpin.IsReadable(node_trigger_mode):
            raise RuntimeError("unable to turn off trigger mode (node retrieval)")

        node_trigger_mode_off = node_trigger_mode.GetEntryByName("Off")
        if not PySpin.IsAvailable(node_trigger_mode_off) or not PySpin.IsReadable(node_trigger_mode_off):
            raise RuntimeError("unable to turn off trigger mode (enum entry retrieval)")

        node_trigger_mode.SetIntValue(node_trigger_mode_off.GetValue())

    def turn_on_trigger_mode(self, stdout=True):
        if stdout:
            print("trigger mode: ON")
        nodemap = self.cam.GetNodeMap()

        node_trigger_mode = PySpin.CEnumerationPtr(nodemap.GetNode("TriggerMode"))
        if not PySpin.IsAvailable(node_trigger_mode) or not PySpin.IsReadable(node_trigger_mode):
            raise RuntimeError("unable to turn on trigger mode (node retrieval)")

        node_trigger_mode_on = node_trigger_mode.GetEntryByName("On")
        if not PySpin.IsAvailable(node_trigger_mode_on) or not PySpin.IsReadable(node_trigger_mode_on):
            raise RuntimeError("unable to turn on trigger mode (enum entry retrieval)")

        node_trigger_mode.SetIntValue(node_trigger_mode_on.GetValue())

    def choose_acquisition_mode(self, acquisition_mode):
        print("acquisition mode: {}".format(acquisition_mode))
        nodemap = self.cam.GetNodeMap()

        node_acquisition_mode = PySpin.CEnumerationPtr(nodemap.GetNode("AcquisitionMode"))
        if not PySpin.IsAvailable(node_acquisition_mode) or not PySpin.IsWritable(node_acquisition_mode):
            raise RuntimeError("unable to set acquisition mode (enum retrieval)")

        node_chosen_mode = node_acquisition_mode.GetEntryByName(acquisition_mode)
        if not PySpin.IsAvailable(node_chosen_mode) or not PySpin.IsReadable(node_chosen_mode):
            raise RuntimeError("unable to set acquisition mode (enum entry retrieval)")

        node_acquisition_mode.SetIntValue(node_chosen_mode.GetValue())

    def choose_auto_exposure_mode(self, auto_exposure_mode):
        if self.cam.ExposureAuto.GetAccessMode() != PySpin.RW:
            raise RuntimeError("unable to change auto exposure mode")

        print("auto exposure mode: {}".format(auto_exposure_mode))
        if auto_exposure_mode is AutoExposureMode.ON:
            self.cam.ExposureAuto.SetValue(PySpin.ExposureAuto_Continuous)
        elif auto_exposure_mode is AutoExposureMode.OFF:
            self.cam.ExposureAuto.SetValue(PySpin.ExposureAuto_Off)

        if self.cam.ExposureMode.GetAccessMode() != PySpin.RW:
            raise RuntimeError("unable to change exposure mode")

        self.cam.ExposureMode.SetValue(PySpin.ExposureMode_Timed)

    def set_exposure_time(self, exposure_time_us):
        exposure_time_us = min(self.cam.ExposureTime.GetMax(), exposure_time_us)
        self.cam.ExposureTime.SetValue(exposure_time_us)
        print("exposure time: {}[us]".format(exposure_time_us))

    def choose_auto_gain_mode(self, auto_gain_mode):
        if self.cam.GainAuto.GetAccessMode() != PySpin.RW:
            raise RuntimeError("unable to change auto gain mode")

        print("auto gain mode: {}".format(auto_gain_mode))
        if auto_gain_mode is AutoGainMode.ON:
            self.cam.GainAuto.SetValue(PySpin.GainAuto_Continuous)
        elif auto_gain_mode is AutoGainMode.OFF:
            self.cam.GainAuto.SetValue(PySpin.GainAuto_Off)

    def set_gain(self, gain_db):
        gain_db = min(self.cam.Gain.GetMax(), gain_db)
        self.cam.Gain.SetValue(gain_db)
        print("gain: {}[dB]".format(gain_db))

    def execute_software_trigger(self):
        if self.cam.TriggerSoftware.GetAccessMode() != PySpin.WO:
            raise RuntimeError("unable to execute trigger")

        # PCからトリガーを送出
        self.cam.TriggerSoftware.Execute()

    def get_next_image(self, pixel_format=PySpin.PixelFormat_Mono8, color_algorithm=PySpin.NO_COLOR_PROCESSING):
        # 画像を転送
        img_captured = self.cam.GetNextImage()
        if img_captured.IsIncomplete():
            print("image incomplete with image status: ".format(img_captured.GetImageStatus()))
            img_captured.Release()
            return None

        # np.arrayに変換
        width = img_captured.GetWidth()
        height = img_captured.GetHeight()
        img_converted = img_captured.Convert(pixel_format, color_algorithm)
        img_captured.Release()

        return img_converted.GetData().reshape(width, height)

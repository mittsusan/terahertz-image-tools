# -*- coding: utf-8 -*-
import enum

import PySpin


class TriggerType(enum.Enum):
    SOFTWARE = 1
    HARDWARE = 2


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

        # トリガーを初期化
        print("initialize trigger type")
        self.choose_trigger_type(trigger_type)

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

    def choose_trigger_type(self, trigger_type):
        if trigger_type is TriggerType.SOFTWARE:
            print("software trigger chosen")
            self.trigger_type = TriggerType.SOFTWARE
        elif trigger_type is TriggerType.HARDWARE:
            print("hardware trigger chosen")
            self.trigger_type = TriggerType.HARDWARE
        else:
            raise RuntimeError("undefined trigger type")
        # トリガーの設定を適用
        self.__apply_trigger_type()

    def __apply_trigger_type(self):
        # トリガーの設定を変更するため，トリガーモードを一時的にOFFにする
        self.turn_off_trigger_mode()

        # トリガーソースを選択
        nodemap = self.cam.GetNodeMap()

        node_trigger_source = PySpin.CEnumerationPtr(nodemap.GetNode("TriggerSource"))
        if not PySpin.IsAvailable(node_trigger_source) or not PySpin.IsWritable(node_trigger_source):
            raise RuntimeError("unable to get trigger source (node retrieval)")

        if self.trigger_type == TriggerType.SOFTWARE:
            node_trigger_source_software = node_trigger_source.GetEntryByName("Software")
            if not PySpin.IsAvailable(node_trigger_source_software) \
               or not PySpin.IsReadable(node_trigger_source_software):
                raise RuntimeError("unable to set trigger source (enum entry retrieval)")
            node_trigger_source.SetIntValue(node_trigger_source_software.GetValue())
        elif self.trigger_type == TriggerType.HARDWARE:
            node_trigger_source_hardware = node_trigger_source.GetEntryByName('Line0')
            if not PySpin.IsAvailable(node_trigger_source_hardware) \
               or not PySpin.IsReadable(node_trigger_source_hardware):
                raise RuntimeError("unable to set trigger source (enum entry retrieval)")
            node_trigger_source.SetIntValue(node_trigger_source_hardware.GetValue())

        # トリガーモードを再開する
        self.turn_on_trigger_mode()

    def turn_off_trigger_mode(self):
        print("turn off trigger mode")
        nodemap = self.cam.GetNodeMap()

        node_trigger_mode = PySpin.CEnumerationPtr(nodemap.GetNode("TriggerMode"))
        if not PySpin.IsAvailable(node_trigger_mode) or not PySpin.IsReadable(node_trigger_mode):
            raise RuntimeError("unable to turn off trigger mode (node retrieval)")

        node_trigger_mode_off = node_trigger_mode.GetEntryByName("Off")
        if not PySpin.IsAvailable(node_trigger_mode_off) or not PySpin.IsReadable(node_trigger_mode_off):
            raise RuntimeError("unable to turn off trigger mode (enum entry retrieval)")

        node_trigger_mode.SetIntValue(node_trigger_mode_off.GetValue())

    def turn_on_trigger_mode(self):
        print("turn on trigger mode")
        nodemap = self.cam.GetNodeMap()

        node_trigger_mode = PySpin.CEnumerationPtr(nodemap.GetNode("TriggerMode"))
        if not PySpin.IsAvailable(node_trigger_mode) or not PySpin.IsReadable(node_trigger_mode):
            raise RuntimeError("unable to turn on trigger mode (node retrieval)")

        node_trigger_mode_on = node_trigger_mode.GetEntryByName("On")
        if not PySpin.IsAvailable(node_trigger_mode_on) or not PySpin.IsReadable(node_trigger_mode_on):
            raise RuntimeError("unable to turn on trigger mode (enum entry retrieval)")

        node_trigger_mode.SetIntValue(node_trigger_mode_on.GetValue())

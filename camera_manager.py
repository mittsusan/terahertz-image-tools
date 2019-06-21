# -*- coding: utf-8 -*-
import PySpin


class CameraManager:
    def __init__(self):
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
        del self.cam

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

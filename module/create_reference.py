from module.ellipse_detector import Ellipse
from module.ellipse_detector import EllipseDetector
from module.imread_imwrite_japanese import ImreadImwriteJapanese
import argparse
import numpy as np
from pathlib import Path
import cv2


class CreateReference:
    def __init__(self):
        self.im_jp = ImreadImwriteJapanese

    def main(self,input,output,numbeams,minsize,maxsize,binthresh):
        # 楕円検出器
        self.detector = EllipseDetector(minsize, maxsize, binthresh)

        ellipses_list = []
        for ref_img_path in input.glob("*.png"):
            print("detecting ellipses from {} ...".format(ref_img_path))
            # 画像を読み込む
            #ref_img = cv2.imread(str(ref_img_path), cv2.IMREAD_GRAYSCALE)
            ref_img = self.im_jp.imread(str(ref_img_path), cv2.IMREAD_GRAYSCALE)
            # 楕円を検出
            ellipses = self.detector.detect(ref_img)
            print(len(ellipses))
            # ビーム数をチェック
            if len(ellipses) != numbeams:
                print("cannot find {} beams from {}".format(numbeams, ref_img_path))
                continue

            # 平均化のため保存
            ellipses_list.append(ellipses)

        # 楕円パラメータを平均化
        print("averaging ellipse parameters ...")
        ave_ellipses = [Ellipse(((0.0, 0.0), (0.0, 0.0), 0.0))] * numbeams
        for beam in range(numbeams):
            c_x_list = []
            c_y_list = []
            minor_ax_list = []
            major_ax_list = []
            angle_list = []
            for ellipses in ellipses_list:
                c_x_list.append(ellipses[beam].c_x)
                c_y_list.append(ellipses[beam].c_y)
                minor_ax_list.append(ellipses[beam].minor_ax)
                major_ax_list.append(ellipses[beam].major_ax)
                angle_list.append(ellipses[beam].angle)
            ave_ellipses[beam].c_x = np.mean(c_x_list)
            ave_ellipses[beam].c_y = np.mean(c_y_list)
            ave_ellipses[beam].minor_ax = np.mean(minor_ax_list)
            ave_ellipses[beam].major_ax = np.mean(major_ax_list)
            ave_ellipses[beam].angle = np.median(angle_list)  # 角度は不連続点の問題があるためmedianを用いる
            print("")
            print("[beam {}]".format(beam))
            print(ave_ellipses[beam])
        print("")

        # 楕円マスクの可視化
        print("integrating ellipse masks ...")
        masks = self.detector.create_ellipse_masks(ellipses, ref_img.shape)
        #int_mask = self.detector.integrate_ellipse_masks(masks, ellipses)
        #int_mask = cv2.resize(int_mask, None, fx=0.5, fy=0.5)
        #cv2.imshow("integrated ellipses", int_mask)
        #cv2.waitKey(0)

        # 保存
        if output is not None:
            print("saving ellipse information to {} ...".format(output.resolve()))
            output.mkdir(parents=True, exist_ok=True)
            for i, (ellipse, mask) in enumerate(zip(ellipses, masks)):
                # 楕円マスクを保存
                #cv2.imwrite(str(output / "{:02d}.png".format(i)), mask)
                self.im_jp.imwrite(str(output / "{:02d}.png".format(i)), mask)
                # (中心x, 中心y, 短軸長, 長軸長, 回転角)の順で保存
                np.savetxt(str(output / "{:02d}.txt".format(i)),
                           np.array([ellipse.c_x, ellipse.c_y, ellipse.minor_ax, ellipse.major_ax, ellipse.angle]),
                           fmt="%.18f", encoding='utf-8')
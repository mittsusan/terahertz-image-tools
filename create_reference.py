from module.ellipse_detector import Ellipse
from module.ellipse_detector import EllipseDetector

import argparse
import numpy as np
from pathlib import Path

import cv2

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("input", type=Path, help="directory path which contains reference images")
    parser.add_argument("--output", default=None, type=Path, help="directory path to save reference information")
    parser.add_argument("--num-beams", default=3, type=int, help="the number of beams")
    parser.add_argument("--min-size", default=100, type=int, help="minumum length of minor axes")
    parser.add_argument("--max-size", default=10000, type=int, help="maximum length of minor axes")
    parser.add_argument("--bin-thresh", default=0, type=int, metavar="THRESH",
                        help="threshold for binarization (if zero, Otsu's method will be used)")
    args = parser.parse_args()

    # 楕円検出器
    detector = EllipseDetector(args.min_size, args.max_size, args.bin_thresh)

    ellipses_list = []
    for ref_img_path in args.input.glob("*.png"):
        print("detecting ellipses from {} ...".format(ref_img_path))
        # 画像を読み込む
        ref_img = cv2.imread(str(ref_img_path), cv2.IMREAD_GRAYSCALE)
        # 楕円を検出
        ellipses = detector.detect(ref_img)

        # ビーム数をチェック
        if len(ellipses) != args.num_beams:
            print("cannot find {} beams from {}".format(args.num_beams, ref_img_path))
            continue

        # 平均化のため保存
        ellipses_list.append(ellipses)

    # 楕円パラメータを平均化
    print("averaging ellipse parameters ...")
    ave_ellipses = [Ellipse(((0.0, 0.0), (0.0, 0.0), 0.0))] * args.num_beams
    for beam in range(args.num_beams):
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
        print("[beam {}]".format(beam))
        print(ave_ellipses[beam])

    # 楕円マスクの可視化
    print("integrating ellipse masks ...")
    masks = detector.create_ellipse_masks(ellipses, ref_img.shape)
    int_mask = detector.integrate_ellipse_masks(masks, ellipses)
    int_mask = cv2.resize(int_mask, None, fx=0.5, fy=0.5)
    cv2.imshow("integrated ellipses", int_mask)
    cv2.waitKey(0)

    # 保存
    if args.output is not None:
        print("saving ellipse information to {} ...".format(args.output.resolve()))
        args.output.mkdir(parents=True, exist_ok=True)
        for i, (ellipse, mask) in enumerate(zip(ellipses, masks)):
            # 楕円マスクを保存
            cv2.imwrite(str(args.output / "{:02d}.png".format(i)), mask)
            # (中心x, 中心y, 短軸長, 長軸長, 回転角)の順で保存
            np.savetxt(str(args.output / "{:02d}.txt".format(i)),
                       np.array([ellipse.c_x, ellipse.c_y, ellipse.minor_ax, ellipse.major_ax, ellipse.angle]),
                       fmt="%.18f")

# -*- coding: utf-8 -*-
import argparse
import numpy as np
from pathlib import Path

import cv2


class Ellipse:
    def __init__(self, ellipse):
        # ellipse = ([中心x, 中心y], [短軸長, 長軸長], 回転角)
        self.c_x = ellipse[0][0]
        self.c_y = ellipse[0][1]
        self.minor_ax = ellipse[1][0]
        self.major_ax = ellipse[1][1]
        self.angle = ellipse[2]

    def __add__(self, other):
        assert type(other) == self.__class__
        return self.__class__(((self.c_x + other.c_x, self.c_y + other.c_y),
                               (self.minor_ax + other.minor_ax, self.major_ax + other.major_ax),
                               self.angle + other.angle))

    def __sub__(self, other):
        assert type(other) == self.__class__
        return self.__class__(((self.c_x - other.c_x, self.c_y - other.c_y),
                               (self.minor_ax - other.minor_ax, self.major_ax - other.major_ax),
                               self.angle - other.angle))

    def __mul__(self, other):
        assert type(other) == int or type(other) == float
        return self.__class__(((self.c_x * other, self.c_y * other),
                               (self.minor_ax * other, self.major_ax * other),
                               self.angle * other))

    def __truediv__(self, other):
        assert type(other) == int or type(other) == float
        return self.__class__(((self.c_x / other, self.c_y / other),
                               (self.minor_ax / other, self.major_ax / other),
                               self.angle / other))

    def __repr__(self):
        return "{:<11}: {}\n".format("center x", self.c_x) + \
               "{:<11}: {}\n".format("center y", self.c_y) + \
               "{:<11}: {}\n".format("minor axis", self.minor_ax) + \
               "{:<11}: {}\n".format("major axis", self.major_ax) + \
               "{:<11}: {}".format("angle", self.angle)

    def create_mask(self, shape):
        ellipse = ((self.c_x, self.c_y), (self.minor_ax, self.major_ax), self.angle)
        return cv2.ellipse(np.zeros(shape[:2]), ellipse, (255, 255, 255), -1, cv2.LINE_4)


class EllipseDetector:
    def __init__(self, min_size=100, max_size=10000, bin_thresh=0):
        self.min_size = min_size
        self.max_size = max_size
        self.bin_thresh = bin_thresh

    def detect(self, img):
        # 二値化
        bin_img = self.__binarize(img)

        # 楕円を検出
        contours = self.__detect_contours(bin_img)
        if len(contours) < 1:
            return None, None
        ellipses = self.__detect_ellipses(contours)

        # 楕円中心のx座標の小さい順にソート
        ellipses = sorted(ellipses, key=lambda x: x.c_x)

        return ellipses

    def __binarize(self, img):
        if 2 < len(img.shape):
            bin_img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        else:
            bin_img = img.copy()
        param = cv2.THRESH_BINARY
        if self.bin_thresh == 0:
            param += cv2.THRESH_OTSU
        _, bin_img = cv2.threshold(bin_img, self.bin_thresh, 255, param)
        return bin_img

    def __detect_contours(self, bin_img):
        if cv2.__version__.startswith("4"):
            contours, _ = cv2.findContours(bin_img, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
        elif cv2.__version__.startswith("3"):
            _, contours, _ = cv2.findContours(bin_img, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
        return contours

    def __detect_ellipses(self, contours):
        ellipses = []
        for i, contour in enumerate(contours):
            # 楕円検出には最低5点以上必要
            if len(contour) < 5:
                continue
            ellipse = Ellipse(cv2.fitEllipse(contour))
            # 短軸の長さで判定
            if ellipse.minor_ax < self.min_size or self.max_size < ellipse.minor_ax:
                continue
            ellipses.append(ellipse)
        return ellipses

    @staticmethod
    def create_ellipse_masks(ellipses, shape):
        masks = []
        for ellipse in ellipses:
            assert type(ellipse) == Ellipse
            masks.append(ellipse.create_mask(shape))
        return masks

    @staticmethod
    def integrate_ellipse_masks(masks, ellipses=None):
        int_mask = sum(masks)
        if ellipses is None:
            return int_mask
        for i, ellipse in enumerate(ellipses):
            assert type(ellipse) == Ellipse
            text_size = cv2.getTextSize(str(i), cv2.FONT_HERSHEY_SIMPLEX, fontScale=1.3, thickness=3)
            pos = (int(ellipse.c_x - text_size[0][0] / 2), int(ellipse.c_y + text_size[0][1] / 2))
            cv2.putText(int_mask, str(i), pos, cv2.FONT_HERSHEY_SIMPLEX, fontScale=1.3, thickness=3, color=(0, 0, 0))
        return int_mask


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("input", type=Path, help="image file path")
    parser.add_argument("--output", type=Path, default=None, help="directory path to dump ellipses")
    parser.add_argument("--min-size", default=100, type=int, help="minumum length of minor axes")
    parser.add_argument("--max-size", default=10000, type=int, help="maximum length of minor axes")
    parser.add_argument("--bin-thresh", default=0, type=int, metavar="THRESH",
                        help="threshold for binarization (if zero, Otsu's method will be used)")
    args = parser.parse_args()

    # 画像を読み込む
    img = cv2.imread(str(args.input))

    # 楕円を検出
    detector = EllipseDetector(args.min_size, args.max_size, args.bin_thresh)
    ellipses = detector.detect(img)

    # 楕円マスクを作成
    masks = detector.create_ellipse_masks(ellipses, img.shape)

    # 楕円マスクを統合
    int_mask = detector.integrate_ellipse_masks(masks, ellipses)

    # 表示
    img = cv2.resize(img, None, fx=0.5, fy=0.5)
    cv2.imshow("input", img)
    int_mask = cv2.resize(int_mask, None, fx=0.5, fy=0.5)
    cv2.imshow("ellipses", int_mask)
    cv2.waitKey(0)

    # 保存
    if args.output is not None:
        args.output.mkdir(parents=True, exist_ok=True)
        for i, (ellipse, mask) in enumerate(zip(ellipses, masks)):
            # 楕円マスクを保存
            cv2.imwrite(str(args.output / "{:02d}.png".format(i)), mask)
            # (中心x, 中心y, 短軸長, 長軸長, 回転角)の順で保存
            np.savetxt(str(args.output / "{:02d}.txt".format(i)),
                       np.array([ellipse.c_x, ellipse.c_y, ellipse.minor_ax, ellipse.major_ax, ellipse.angle]),
                       fmt="%.18f")

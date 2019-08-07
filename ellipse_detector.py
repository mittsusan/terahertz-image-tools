# -*- coding: utf-8 -*-
import argparse
import numpy as np
from pathlib import Path

import cv2


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
        # ellipse = ([中心x, 中心y], [短軸長, 長軸長], 回転角)
        ellipses = sorted(ellipses, key=lambda x: x[0][0])

        # 楕円画像を作成
        ellipse_imgs = self.__create_ellipse_images(ellipses, bin_img.shape)

        return ellipses, ellipse_imgs

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
            ellipse = cv2.fitEllipse(contour)
            # 短軸の長さで判定
            # ellipse = ([中心x, 中心y], [短軸長, 長軸長], 回転角)
            if ellipse[1][0] < self.min_size or self.max_size < ellipse[1][0]:
                continue
            ellipses.append(ellipse)
        return ellipses

    def __create_ellipse_images(self, ellipses, shape):
        ellipse_imgs = []
        for ellipse in ellipses:
            # 各楕円について，楕円を白で描画した画像を作成
            ellipse_img = cv2.ellipse(np.zeros(shape), ellipse, (255, 255, 255), -1, cv2.LINE_4)
            ellipse_imgs.append(ellipse_img)
        return ellipse_imgs


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("input", type=Path, help="image file path")
    parser.add_argument("--output", type=Path, default=None, help="output path for ellipses")
    parser.add_argument("--min-size", default=100, type=int, help="minumum length of minor axes")
    parser.add_argument("--max-size", default=10000, type=int, help="maximum length of minor axes")
    parser.add_argument("--bin-thresh", default=0, type=int, help="threshold for binarization (if zero, Otsu's method will be used)")
    args = parser.parse_args()

    img = cv2.imread(str(args.input))

    # 楕円を検出
    detector = EllipseDetector(args.min_size, args.max_size, args.bin_thresh)
    ellipses, imgs = detector.detect(img)

    # 可視化
    int_img = sum(imgs)
    for i, ellipse in enumerate(ellipses):
        pos = (int(ellipse[0][0] - 13), int(ellipse[0][1] + 13))
        cv2.putText(int_img, str(i), pos, cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0, 0, 0), 3)
    img = cv2.resize(img, None, fx=0.5, fy=0.5)
    cv2.imshow("input", img)
    int_img = cv2.resize(int_img, None, fx=0.5, fy=0.5)
    cv2.imshow("ellipses", int_img)
    cv2.waitKey(0)

    # 保存
    if args.output is not None:
        args.output.mkdir(parents=True, exist_ok=True)
        for i, (ellipse, img) in enumerate(zip(ellipses, imgs)):
            cv2.imwrite(str(args.output / "{:02d}.png".format(i)), img)

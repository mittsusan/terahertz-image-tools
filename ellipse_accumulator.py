# -*- coding: utf-8 -*-
import argparse
from pathlib import Path

import cv2


class ReferenceImage:
    def __init__(self, beam_name, ellipse_img):
        self.beam_name = beam_name
        self.ellipse_img = ellipse_img
        self.nonzero_coords = ellipse_img.nonzero()


class EllipseAccumulator:
    def __init__(self, num_beams):
        self.num_beams = num_beams
        self.ref_imgs = []

    def reset_reference(self):
        self.ref_imgs = []

    def append_reference(self, ref_img):
        assert type(ref_img) == ReferenceImage
        self.ref_imgs.append(ref_img)

    def calc_averages(self, img):
        averages = []
        for ref_img in self.ref_imgs:
            average = img[ref_img.nonzero_coords]
            average = average.mean()
            averages.append((ref_img.beam_name, average))
        return averages


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("ref", type=Path, help="directory path which contains reference images of ellipses")
    parser.add_argument("input", type=Path, help="image file path")
    parser.add_argument("--num-beams", default=3, type=int, help="the number of beams")
    args = parser.parse_args()

    accumulator = EllipseAccumulator(args.num_beams)

    # リファレンス画像を読み込んでセット
    for ref_img_path in args.ref.glob("*.png"):
        ref_img = cv2.imread(str(ref_img_path), cv2.IMREAD_GRAYSCALE)
        accumulator.append_reference(ReferenceImage(ref_img_path.stem, ref_img))

    # 入力画像を読み込む
    img = cv2.imread(str(args.input), cv2.IMREAD_GRAYSCALE)

    # 各領域の平均値を計算
    averages = accumulator.calc_averages(img)

    # 可視化
    print("beam name" + " " * 4 + "average")
    print("-" * 30)
    for ave in averages:
        print("{:<13}{}".format(ave[0], ave[1]))

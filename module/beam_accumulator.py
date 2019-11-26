# -*- coding: utf-8 -*-
import argparse
from pathlib import Path

import cv2


class EllipseMask:
    def __init__(self, beam_name, mask):
        self.beam_name = beam_name
        self.mask = mask
        self.nonzero = mask.nonzero()


class BeamAccumulator:
    def __init__(self, num_beams):
        self.num_beams = num_beams
        self.ellipse_masks = []

    def reset_ellipse_masks(self):
        self.ellipse_masks = []

    def append_ellipse_mask(self, ellipse_mask):
        assert type(ellipse_mask) == EllipseMask
        self.ellipse_masks.append(ellipse_mask)

    def calc_averages(self, img):
        averages = []
        for ellipse_mask in self.ellipse_masks:
            average = img[ellipse_mask.nonzero] #一列のリスト
            average = average.mean()
            averages.append((ellipse_mask.beam_name, average))
        return averages

    def fwhm(self, img):
        averages = []
        for ellipse_mask in self.ellipse_masks:
            average = img[ellipse_mask.nonzero]  # 一列のリスト
            average = average.mean()
            averages.append((ellipse_mask.beam_name, average))
        return averages


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("ref", type=Path, help="directory path which contains masks of ellipses")
    parser.add_argument("input", type=Path, help="image file path")
    parser.add_argument("--num-beams", default=3, type=int, help="the number of beams")
    args = parser.parse_args()

    accumulator = BeamAccumulator(args.num_beams)

    # 楕円マスクを読み込んでセット
    accumulator.reset_ellipse_masks()
    for mask_path in args.ref.glob("*.png"):
        mask = cv2.imread(str(mask_path), cv2.IMREAD_GRAYSCALE)
        accumulator.append_ellipse_mask(EllipseMask(mask_path.stem, mask))

    # 入力画像を読み込む
    img = cv2.imread(str(args.input), cv2.IMREAD_GRAYSCALE)

    # 各領域の平均値を計算
    averages = accumulator.calc_averages(img)

    # 可視化
    print("-" * 30)
    print("beam name" + " " * 4 + "average")
    print("-" * 30)
    for ave in averages:
        print("{:<13}{}".format(ave[0], ave[1]))
    print("-" * 30)

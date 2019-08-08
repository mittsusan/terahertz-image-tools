from module.beam_accumulator import EllipseMask
from module.beam_accumulator import BeamAccumulator

import argparse
from pathlib import Path

import cv2

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("ref", type=Path, help="directory path which contains reference information")
    parser.add_argument("input", type=Path, help="directory path which contains images to input")
    parser.add_argument("--num-beams", default=3, type=int, help="the number of beams")
    args = parser.parse_args()

    # 積算器
    accumulator = BeamAccumulator(args.num_beams)

    # 楕円マスクを読み込んでセット
    accumulator.reset_ellipse_masks()
    for mask_path in args.ref.glob("*.png"):
        mask = cv2.imread(str(mask_path), cv2.IMREAD_GRAYSCALE)
        accumulator.append_ellipse_mask(EllipseMask(mask_path.stem, mask))

    # 各画像を読み込んで各楕円マスク内のピクセル値を平均する
    for img_path in args.input.glob("*.png"):
        # 入力画像を読み込む
        img = cv2.imread(str(img_path), cv2.IMREAD_GRAYSCALE)

        # 各領域の平均値を計算
        averages = accumulator.calc_averages(img)

        # 可視化
        print("")
        print("image: {}".format(img_path.resolve()))
        print("-" * 30)
        print("beam name" + " " * 4 + "average")
        print("-" * 30)
        for ave in averages:
            print("{:<13}{}".format(ave[0], ave[1]))
        print("-" * 30)

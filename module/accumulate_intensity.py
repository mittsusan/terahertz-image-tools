from module.beam_accumulator import EllipseMask
from module.beam_accumulator import BeamAccumulator

import cv2
import os
import numpy as np
from pathlib import Path

class AccumulateIntensity:

    def main(self,ref,input,output,num_beams):

        # 積算器
        accumulator = BeamAccumulator(num_beams)

        # 楕円マスクを読み込んでセット
        accumulator.reset_ellipse_masks()
        for mask_path in ref.glob("*.png"):
            mask = cv2.imread(str(mask_path), cv2.IMREAD_GRAYSCALE)
            accumulator.append_ellipse_mask(EllipseMask(mask_path.stem, mask))

        # 各画像を読み込んで各楕円マスク内のピクセル値を平均する
        for img_path in input.glob("*.png"):
            basename = os.path.basename(img_path)
            root, ext = os.path.splitext(basename)
            # 入力画像を読み込む
            img = cv2.imread(str(img_path), cv2.IMREAD_GRAYSCALE)

            # 各領域の平均値を計算
            averages = accumulator.calc_averages(img)
            listave = []
            for ave in averages:
                    listave.append(ave[1])

            #テキストファイルに保存
            numpyave = np.array(listave)
            np.savetxt(output,numpyave)


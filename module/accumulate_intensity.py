from module.beam_accumulator import EllipseMask
from module.beam_accumulator import BeamAccumulator
from module.imread_imwrite_japanese import ImreadImwriteJapanese
import cv2
import os
import numpy as np
#from pathlib import Path

class AccumulateIntensity:
    def __init__(self):
        self.im_jp = ImreadImwriteJapanese

    def main(self,ref,input,output,num_beams):

        # 積算器
        accumulator = BeamAccumulator(num_beams)

        # 楕円マスクを読み込んでセット
        accumulator.reset_ellipse_masks()
        for mask_path in ref.glob("*.png"):
            #mask = cv2.imread(str(mask_path), cv2.IMREAD_GRAYSCALE)
            mask = self.im_jp.imread(str(mask_path), cv2.IMREAD_GRAYSCALE)
            accumulator.append_ellipse_mask(EllipseMask(mask_path.stem, mask))

        # 各画像を読み込んで各楕円マスク内のピクセル値を平均する
        for img_path in input.glob("*.png"):
            basename = os.path.basename(img_path)
            root, ext = os.path.splitext(basename)
            # 入力画像を読み込む
            #img = cv2.imread(str(img_path), cv2.IMREAD_GRAYSCALE)
            img = self.im_jp.imread(str(img_path), cv2.IMREAD_GRAYSCALE)
            # 各領域の平均値を計算
            averages = accumulator.calc_averages(img)
            listave = []
            for ave in averages:
                listave.append(ave[1])
            txtname = root + '.txt'
            output_path = os.path.join(output,txtname)
            #テキストファイルに保存
            numpyave = np.array(listave)
            print(output_path)
            print(numpyave)
            np.savetxt(output_path, numpyave, delimiter='\t', encoding='utf-8')
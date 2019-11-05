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

            # 可視化
            '''
            print("")
            print("image: {}".format(img_path.resolve()))
            print("-" * 30)
            print("beam name" + " " * 4 + "average")
            print("-" * 30)
            '''
            listave = []
            for ave in averages:
                #print("{:<13}{}".format(ave[0], ave[1]))
                    listave.append(ave[1])
                    print(ave[1])
            #print("-" * 30)

            #テキストファイルに保存
            print(listave)

            outputdir = output + '/{}.txt'.format(root)
            print(outputdir)
            print(type(outputdir))
            numpyave = np.array(listave)
            np.savetxt(outputdir,numpyave)


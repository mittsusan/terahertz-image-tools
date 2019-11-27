from module.ellipse_detector import Ellipse
from module.ellipse_detector import EllipseDetector
from module.imread_imwrite_japanese import ImreadImwriteJapanese
import argparse
import numpy as np
from pathlib import Path
import cv2
import os
from scipy.stats import norm


class FWHM:
    def __init__(self):
        self.im_jp = ImreadImwriteJapanese

    def fwhm(self, ref, input, output):
        ellipses = []
        for ellipse in ref.glob('*.txt'):
            npparam_ellipse = np.loadtxt(fname=ellipse, delimiter='\t', encoding='utf-8')
            insertnpparam_ellipse = [[npparam_ellipse[0], npparam_ellipse[1]], [npparam_ellipse[2], npparam_ellipse[3]], npparam_ellipse[4]]
            ellipses.append(Ellipse(insertnpparam_ellipse))

        # 各画像を読み込んで長軸、短軸のピクセル値を抽出
        pixel_size = 0.0055
        for img_path in input.glob("*.png"):
            basename = os.path.basename(img_path)
            root, ext = os.path.splitext(basename)
            # 入力画像を読み込む
            # img = cv2.imread(str(img_path), cv2.IMREAD_GRAYSCALE)
            img = self.im_jp.imread(str(img_path), cv2.IMREAD_GRAYSCALE)
            minor_ax_pixels = []
            major_ax_pixels = []
            fwhm_minors = []
            fwhm_majors = []
            for i, ellipse in enumerate(ellipses):
                # 高さを定義
                height = img.shape[0]
                # 幅を定義
                width = img.shape[1]
                # 回転角を指定
                angle = ellipse.angle
                # スケールを指定
                scale = 1.0
                # 回転の中心を指定
                center = (ellipse.c_x, ellipse.c_y)
                # getRotationMatrix2D関数を使用
                trans = cv2.getRotationMatrix2D(center, angle, scale)
                # アフィン変換
                affine_image = cv2.warpAffine(img, trans, (width, height))
                minor_ax_left_point = int(ellipse.c_x-ellipse.minor_ax/2)
                minor_ax_right_point = int(ellipse.c_x+ellipse.minor_ax/2)
                major_ax_top_point = int(ellipse.c_y-ellipse.major_ax/2)
                major_ax_bottom_point = int(ellipse.c_y+ellipse.major_ax/2)
                minor_ax_pixel = affine_image[int(ellipse.c_y), minor_ax_left_point:minor_ax_right_point]
                major_ax_pixel = affine_image[major_ax_top_point:major_ax_bottom_point, int(ellipse.c_x)]

                # ガウスフィッテング
                param_minor = norm.fit(minor_ax_pixel)
                param_major = norm.fit(major_ax_pixel)
                # FWHM
                fwhm_minor = 2.35 * param_minor[1] * pixel_size
                fwhm_major = 2.35 * param_major[1] * pixel_size
                minor_ax_pixels.append(len(minor_ax_pixel) * pixel_size)
                major_ax_pixels.append(len(major_ax_pixel) * pixel_size)
                fwhm_minors.append(fwhm_minor)
                fwhm_majors.append(fwhm_major)
                affine_image = cv2.line(affine_image, (minor_ax_left_point, int(ellipse.c_y)),
                                        (minor_ax_right_point, int(ellipse.c_y)), (255, 255, 255), 5)  # 短軸は青色
                affine_image = cv2.line(affine_image, (int(ellipse.c_x), major_ax_top_point),
                                        (int(ellipse.c_x), major_ax_bottom_point), (255, 255, 255), 5)  # 長軸は赤色
                ellipse = ((ellipse.c_x, ellipse.c_y), (ellipse.minor_ax, ellipse.major_ax), 0)
                affine_image = cv2.ellipse(affine_image, ellipse, (255, 255, 255), thickness=5)
                affine_name = str(i) + '_' + basename
                output_path_affine = os.path.join(output, affine_name)
                self.im_jp.imwrite(output_path_affine, affine_image)
            minor_ax_pixels = np.array(minor_ax_pixels)
            major_ax_pixels = np.array(major_ax_pixels)
            fwhm_minors = np.array(fwhm_minors)
            fwhm_majors = np.array(fwhm_majors)

            param_ellipse = np.vstack((minor_ax_pixels, major_ax_pixels, fwhm_minors, fwhm_majors))
            txtname = root + '.txt'
            output_path = os.path.join(output, txtname)
            # テキストファイルに保存
            print("saving ellipse information to {} ...".format(output_path))
            np.savetxt(output_path, param_ellipse, delimiter='\t', encoding='utf-8')

    def realtime_fwhm(self, frame, ellipses):

        # 各画像を読み込んで長軸、短軸のピクセル値を抽出
        pixel_size = 0.0055
        font = cv2.FONT_HERSHEY_PLAIN
        fontsize = 3
        samplename_position_x = 50
        samplename_position_y = 100
        font_scale = 2
        xmove = 750
        ymove = 50
        for i, ellipse in enumerate(ellipses):
            # 高さを定義
            height = frame.shape[0]
            # 幅を定義
            width = frame.shape[1]
            # 回転角を指定
            angle = ellipse.angle
            # スケールを指定
            scale = 1.0
            # 回転の中心を指定
            center = (ellipse.c_x, ellipse.c_y)
            # getRotationMatrix2D関数を使用
            trans = cv2.getRotationMatrix2D(center, angle, scale)
            # アフィン変換
            affine_image = cv2.warpAffine(frame, trans, (width, height))
            #print('affineimage')
            #print(affine_image.shape)
            minor_ax_left_point = int(ellipse.c_x - ellipse.minor_ax / 2)
            minor_ax_right_point = int(ellipse.c_x + ellipse.minor_ax / 2)
            major_ax_top_point = int(ellipse.c_y - ellipse.major_ax / 2)
            major_ax_bottom_point = int(ellipse.c_y + ellipse.major_ax / 2)
            minor_ax_pixel = affine_image[int(ellipse.c_y), minor_ax_left_point:minor_ax_right_point]
            major_ax_pixel = affine_image[major_ax_top_point:major_ax_bottom_point, int(ellipse.c_x)]

            # ガウスフィッテング
            param_minor = norm.fit(minor_ax_pixel)
            param_major = norm.fit(major_ax_pixel)
            # FWHM
            fwhm_minor = 2.35 * param_minor[1] * pixel_size
            fwhm_major = 2.35 * param_major[1] * pixel_size

            cv2.putText(frame, 'Short axis:{:.5f}mm'.format(len(minor_ax_pixel) * pixel_size),
                        (samplename_position_x + i*xmove, samplename_position_y), font, fontsize,
                        (255, 255, 255), font_scale, cv2.LINE_AA)
            cv2.putText(frame, 'Long axis:{:.5f}mm'.format(len(major_ax_pixel) * pixel_size),
                        (samplename_position_x + i*xmove, samplename_position_y + ymove), font, fontsize,
                        (255, 255, 255), font_scale, cv2.LINE_AA)
            cv2.putText(frame, 'FWHM Short axis:{:.5f}mm'.format(fwhm_minor),
                        (samplename_position_x + i*xmove, samplename_position_y + ymove*2), font, fontsize,
                        (255, 255, 255), font_scale, cv2.LINE_AA)
            cv2.putText(frame, 'FWHM Long axis:{:.5f}mm'.format(fwhm_major),
                        (samplename_position_x + i*xmove, samplename_position_y + ymove*3), font, fontsize,
                        (255, 255, 255), font_scale, cv2.LINE_AA)
            ellipse = ((ellipse.c_x, ellipse.c_y), (ellipse.minor_ax, ellipse.major_ax), 0)
            cv2.ellipse(frame, ellipse, (255, 255, 255), thickness=5)
            '''
            affine_image = cv2.line(affine_image, (minor_ax_left_point, int(ellipse.c_y)),
                                    (minor_ax_right_point, int(ellipse.c_y)), (255, 255, 255), 5)  # 短軸は青色
            affine_image = cv2.line(affine_image, (int(ellipse.c_x), major_ax_top_point),
                                    (int(ellipse.c_x), major_ax_bottom_point), (255, 255, 255), 5)  # 長軸は赤色
            '''

        return frame
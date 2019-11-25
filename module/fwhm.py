from module.ellipse_detector import Ellipse
from module.ellipse_detector import EllipseDetector
from module.imread_imwrite_japanese import ImreadImwriteJapanese
import argparse
import numpy as np
from pathlib import Path
import cv2


class FWHM:
    def __init__(self):
        self.im_jp = ImreadImwriteJapanese

    def fwhm(self):
        # 楕円検出器
        self.detector= EllipseDetector(minsize, maxsize, binthresh)
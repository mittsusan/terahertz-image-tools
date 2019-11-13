import time
import cv2
from PIL import Image,ImageTk
import os

class ShowBeamInGUI:
    def showbeam_ingui(self, trigger, gain, exp):
        while True:
            # 処理前の時刻
            t1 = time.time()

            self.cvv.cameraFrame(trigger, gain, exp)
            if self.savecount != 0:
                savepath = os.path.join(self.savepath + '/{}.png'.format(self.savecount))
                cv2.imwrite(savepath, self.cvv.frame)
                self.savecount += -1
                print('saveimage:{}'.format(self.savecount))
            self.loop_img = Image.fromarray(self.cvv.frame)
            self.canvas_img = ImageTk.PhotoImage(self.loop_img)
            self.canvas.create_image(self.CANVAS_X / 2, self.CANVAS_Y / 2, image=self.canvas_img)
            # self._job = self.root.after(10, self.afterMSec(trigger,gain,exp))
            if self.cancelflag:
                print('Complete Cancel')
                self.cancelflag = False
                break

            # 処理後の時刻
            t2 = time.time()

            # 経過時間を表示
            freq = 1 / (t2 - t1)
            print(f"フレームレート：{freq}fps")
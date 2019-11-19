import  glob
import numpy as np
import os

class ArrangeValue:
    def __init__(self,output):
        self.output = output

    def arrange_value(self):
        # ファイルのパスの読み込み
        flag = False
        path_list = glob.glob(self.output + '/*')
        for i in path_list:
            if flag == False:
                beam_accum = np.loadtxt(fname=i)
                flag = True
            else:
                beam_accum_add = np.loadtxt(fname=i)
                beam_accum = np.vstack((beam_accum, beam_accum_add))
        print(beam_accum)
        np.savetxt(os.path.join(self.output, 'stability.txt'), beam_accum)
        print('Save stability')

import tkinter as tk
import threading
from PIL import Image,ImageTk
import cv2
import numpy as np
from module.camera_manager import CameraManager
from module.camera_manager import TriggerType
from module.camera_manager import AcquisitionMode
from module.camera_manager import AutoExposureMode
from module.camera_manager import AutoGainMode
import tkinter.filedialog as tkfd

class GUI:
    def __init__(self):
        self.cvv=Show_Infrared_Camera()
        self.root=tk.Tk()
        self._job = None
        self.cancelflag = False
        self.savecount = 0
        self.ROOT_X = 1000
        self.ROOT_Y = 700
        self.CANVAS_X=640
        self.CANVAS_Y=480
        self.root.title(u"RealtimeBeamImage")
        self.root.geometry(str(self.ROOT_X) + "x" + str(self.ROOT_Y))
        self.root.resizable(width=0, height=0)
        self.savepath = ''
        self.firstFrame()#トリガー、ゲイン、露出、保存を決めるフレーム
        self.secondFrame()#リアルタイムの画像を表示させるフレーム



    def afterMSec(self,trigger,gain,exp):

        while True:
            self.cvv.cameraFrame(trigger,gain,exp)
            if self.savecount != 0:
                cv2.imwrite(self.savepath + '/{}.png'.format(self.savecount), self.cvv.frame)
                self.savecount += -1
                print('saveimage:{}'.format(self.savecount))
            self.loop_img = Image.fromarray(self.cvv.frame)
            self.canvas_img = ImageTk.PhotoImage(self.loop_img)
            self.canvas.create_image(self.CANVAS_X / 2, self.CANVAS_Y / 2, image=self.canvas_img)
            #self._job = self.root.after(10, self.afterMSec(trigger,gain,exp))
            if self.cancelflag:
                print('Complete Cancel')
                self.cancelflag = False
                break

    def cancel(self):
        self.cancelflag = True

    def firstFrame(self):

        # ラベル
        lbl = tk.Label(text='トリガータイプを選択してください。')
        lbl.place(x=30, y=30)
        lbl = tk.Label(text='ゲイン[db]を選択してください。')
        lbl.place(x=30, y=70)
        lbl = tk.Label(text='露出[um]を選択してください。')
        lbl.place(x=30, y=90)
        lbl = tk.Label(text='保存先を選択してください。')
        lbl.place(x=400, y=30)
        lbl = tk.Label(text='保存数を選択してください。')
        lbl.place(x=400, y=60)

        # ラジオボタンのラベルをリスト化する
        rdo_txt = ['software', 'hardware']
        # ラジオボタンの状態
        rdo_var = tk.IntVar()
        # ラジオボタンを動的に作成して配置
        for i in range(len(rdo_txt)):
            rdo = tk.Radiobutton(self.root, value=i, variable=rdo_var, text=rdo_txt[i])
            rdo.place(x=200, y=15 + (i * 24))



        # ゲインのテキストボックスを出現させる
        gainEntry = tk.Entry(width=20)  # widthプロパティで大きさを変える
        gainEntry.insert(tk.END, u'10')  # 最初から文字を入れておく
        gainEntry.place(x=200, y=70)

        # 露出のテキストボックスを出現させる
        expEntry = tk.Entry(width=20)  # widthプロパティで大きさを変える
        expEntry.insert(tk.END, u'20000')  # 最初から文字を入れておく
        expEntry.place(x=200, y=90)

        # 保存先のテキストボックスを出現させる
        saveEntry = tk.Entry(width=40)  # widthプロパティで大きさを変える
        saveEntry.place(x=550, y=30)

        # 保存数のテキストボックスを出現させる
        numEntry = tk.Entry(width=20)  # widthプロパティで大きさを変える
        numEntry.insert(tk.END, u'10')  # 最初から文字を入れておく
        numEntry.place(x=550, y=60)




        def button1_clicked():
            # 値を取得
            trigger_type = rdo_txt[rdo_var.get()]

            gainEntry_value = gainEntry.get()
            gainEntry_value = int(gainEntry_value)
            expEntry_value = expEntry.get()
            expEntry_value = int(expEntry_value)
            self.cvv.configure(trigger_type,gainEntry_value,expEntry_value)
            th = threading.Thread(target=self.afterMSec, args=(trigger_type,gainEntry_value,expEntry_value))
            th.start()
            button1.config(state="disabled")
            button2.config(state="active")
            save.config(state="active")


        def button2_clicked():
            self.cancel()
            print('Cancel')
            button2.config(state="disabled")
            button3.config(state="active")
            save.config(state="disabled")

        def button3_clicked():
            self.cvv.cam_manager.stop_acquisition()
            print('Stop')
            button3.config(state="disabled")
            button1.config(state="active")

        def selectdir_clicked():
            self.savepath = tkfd.askdirectory(initialdir='/')
            saveEntry.insert(tk.END, self.savepath)
            print('Select')
            print(self.savepath)

        def save_clicked():
            numEntry_value = gainEntry.get()
            self.savecount = int(numEntry_value)
            print('Save')



        button1 = tk.Button(text='OK',command=button1_clicked)
        button1.place(x=50, y=110)

        button2 = tk.Button(text='Cancel', command=button2_clicked,state='disabled')
        button2.place(x=90, y=110)

        button3 = tk.Button(text='STOP', command=button3_clicked,state='disabled')
        button3.place(x=150, y=110)

        selectdir = tk.Button(text='Select', command=selectdir_clicked)
        selectdir.place(x=800, y=25)

        save = tk.Button(text='Save', command=save_clicked,state='disabled')
        save.place(x=480, y=80)



    def secondFrame(self):
        #動画生成の為のキャンバスを作る
        self.canvas = tk.Canvas(self.root, width=self.CANVAS_X, height=self.CANVAS_Y)
        self.canvas.create_rectangle(0, 0, self.CANVAS_X, self.CANVAS_Y, fill="#696969")
        self.canvas.place(x=300, y=200)




class Show_Infrared_Camera:
    def __init__(self):
        self.cam_manager = CameraManager()
    def configure(self,trigger,gain,exp):


        if trigger == "software":
            self.cam_manager.choose_trigger_type(TriggerType.SOFTWARE)
        elif trigger == "hardware":
            self.cam_manager.choose_trigger_type(TriggerType.HARDWARE)

        self.cam_manager.turn_on_trigger_mode()

        self.cam_manager.choose_acquisition_mode(AcquisitionMode.CONTINUOUS)

        self.cam_manager.choose_auto_exposure_mode(AutoExposureMode.OFF)
        self.cam_manager.set_exposure_time(exp)

        self.cam_manager.choose_auto_gain_mode(AutoGainMode.OFF)
        self.cam_manager.set_gain(gain)

        self.cam_manager.start_acquisition()

    def cameraFrame(self,trigger,gain,exp):

        if trigger == "software":
            self.cam_manager.execute_software_trigger()

        self.frame = self.cam_manager.get_next_image()
        #self.frame = cv2.cvtColor(self.frame, cv2.COLOR_BGR2RGB)



class Main:
    def __init__(self):
        self.gui=GUI()
        self.gui.root.mainloop()


if __name__=="__main__":
    Main()

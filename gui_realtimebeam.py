import tkinter as tk
import threading
from PIL import Image,ImageTk
import cv2
import numpy as np

import tkinter.filedialog as tkfd
import time

from pathlib import Path
from module.create_reference import CreateReference
from module.show_infrared_camera import ShowInfraredCamera
from module.accumulate_intensity import AccumulateIntensity

class GUI:
    def __init__(self):
        self.cvv=ShowInfraredCamera()
        self.create_reference = CreateReference()
        self.accumulate_intensity = AccumulateIntensity()
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
        self.inputpath = ''
        self.outputpath = ''
        self.accum_inputpath = ''
        self.firstFrame()#トリガー、ゲイン、露出、保存を決めるフレーム
        #self.secondFrame()#リアルタイムの画像を表示させるフレーム
        self.ellipseFrame()



    def showbeam_ingui(self,trigger,gain,exp):

        while True:
            # 処理前の時刻
            t1 = time.time()

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

            # 処理後の時刻
            t2 = time.time()

            # 経過時間を表示
            freq = 1/(t2 - t1)
            print(f"フレームレート：{freq}fps")

    def showbeam_imshow(self,trigger,gain,exp):
        while True:
            # 処理前の時刻
            t1 = time.time()
            self.cvv.cameraFrame(trigger,gain,exp)
            if self.savecount != 0:
                cv2.imwrite(self.savepath + '/{}.png'.format(self.savecount), self.cvv.frame)
                self.savecount += -1
                print('saveimage:{}'.format(self.savecount))

            if self.cvv.frame is None:
                continue

            cv2.imshow("Showing image(閉じる際はqボタンを押してください)", cv2.resize(self.cvv.frame, (1024, 1024)))

            if cv2.waitKey(1) & 0xFF == ord('q'):
                cv2.destroyAllWindows()
                print('Complete Cancel')

                self.button2.config(state="disabled")
                self.button3.config(state="active")
                self.save.config(state="disabled")
                break
            '''
            if self.cancelflag:
                cv2.destroyAllWindows()
                self.cancelflag = False
                print('Complete Cancel')

                break
            '''

            # 処理後の時刻
            t2 = time.time()

            # 経過時間を表示
            freq = 1 / (t2 - t1)
            print(f"フレームレート：{freq}fps")

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
        gainEntry.insert(tk.END, u'0')  # 最初から文字を入れておく
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
            th = threading.Thread(target=self.showbeam_imshow, args=(trigger_type,gainEntry_value,expEntry_value))
            th.start()
            self.button1.config(state="disabled")
            self.button2.config(state="active")
            self.save.config(state="active")


        def button2_clicked():
            self.cancel()
            print('Cancel')
            self.button2.config(state="disabled")
            self.button3.config(state="active")
            self.save.config(state="disabled")

        def button3_clicked():
            self.cvv.cam_manager.stop_acquisition()
            print('Stop')
            self.button3.config(state="disabled")
            self.button1.config(state="active")

        def selectdir_clicked():
            self.savepath = tkfd.askdirectory(initialdir='/')
            saveEntry.insert(tk.END, self.savepath)
            print('Select')
            print(self.savepath)

        def save_clicked():
            numEntry_value = gainEntry.get()
            self.savecount = int(numEntry_value)
            print('Save')



        self.button1 = tk.Button(text='OK',command=button1_clicked)
        self.button1.place(x=50, y=110)

        self.button2 = tk.Button(text='Cancel', command=button2_clicked,state='disabled')
        self.button2.place(x=90, y=110)

        self.button3 = tk.Button(text='STOP', command=button3_clicked,state='disabled')
        self.button3.place(x=150, y=110)

        self.selectdir = tk.Button(text='Select', command=selectdir_clicked)
        self.selectdir.place(x=800, y=25)

        self.save = tk.Button(text='Save', command=save_clicked,state='disabled')
        self.save.place(x=480, y=80)



    def secondFrame(self):
        #動画生成の為のキャンバスを作る
        self.canvas = tk.Canvas(self.root, width=self.CANVAS_X, height=self.CANVAS_Y)
        self.canvas.create_rectangle(0, 0, self.CANVAS_X, self.CANVAS_Y, fill="#696969")
        self.canvas.place(x=300, y=200)

    def ellipseFrame(self):
        # ラベル
        labelx = 30
        labely = 200
        txtmovex = 470
        lbl = tk.Label(text='楕円検出用リファレンス画像を保存したディレクトリを選択してください。')
        lbl.place(x=labelx, y=labely)
        lbl = tk.Label(text='楕円パラメータと楕円マスクを保存するディレクトリを選択してください。(楕円積算にも使用!!)')
        lbl.place(x=labelx, y=labely+20)
        lbl = tk.Label(text='ビームの本数を選択してください(楕円積算にも使用!!)')
        lbl.place(x=labelx, y=labely+40)
        lbl = tk.Label(text='楕円の短軸長の最小閾値を選択してください。')
        lbl.place(x=labelx, y=labely+60)
        lbl = tk.Label(text='楕円の短軸長の最大閾値を選択してください。')
        lbl.place(x=labelx, y=labely+80)
        lbl = tk.Label(text='二値化の閾値 (0の場合，Otsus methodが使われる)を選択してください。')
        lbl.place(x=labelx, y=labely+100)
        lbl = tk.Label(text='積算したい入力画像を格納したディレクトリを選択してください。')
        lbl.place(x=labelx, y=labely + 150)


        # テキストボックス
        inputEntry = tk.Entry(width=40)  # widthプロパティで大きさを変える
        inputEntry.place(x=labelx+txtmovex, y=labely)
        outputEntry = tk.Entry(width=40)  # widthプロパティで大きさを変える
        outputEntry.place(x=labelx+txtmovex, y=labely+20)
        beamsEntry = tk.Entry(width=10)  # widthプロパティで大きさを変える
        beamsEntry.insert(tk.END, u'3')  # 最初から文字を入れておく
        beamsEntry.place(x=labelx+txtmovex, y=labely +40)
        minEntry = tk.Entry(width=10)  # widthプロパティで大きさを変える
        minEntry.insert(tk.END, u'100')  # 最初から文字を入れておく
        minEntry.place(x=labelx+txtmovex, y=labely +60)
        maxEntry = tk.Entry(width=10)  # widthプロパティで大きさを変える
        maxEntry.insert(tk.END, u'10000')  # 最初から文字を入れておく
        maxEntry.place(x=labelx+txtmovex, y=labely +80)
        threshEntry = tk.Entry(width=10)  # widthプロパティで大きさを変える
        threshEntry.insert(tk.END, u'0')  # 最初から文字を入れておく
        threshEntry.place(x=labelx+txtmovex, y=labely +100)
        accuminputEntry = tk.Entry(width=40)  # widthプロパティで大きさを変える
        accuminputEntry.place(x=labelx + txtmovex, y=labely + 150)

        def inputdir_clicked():
            self.inputpath = tkfd.askdirectory(initialdir='/')
            inputEntry.insert(tk.END, self.inputpath)
            print('Select')
            print(self.inputpath)

        def outputdir_clicked():
            self.outputpath = tkfd.askdirectory(initialdir='/')
            outputEntry.insert(tk.END, self.outputpath)
            print('Select')
            print(self.outputpath)

        def getref_ellipse_clicked():
            input = Path(inputEntry.get())
            output = Path(outputEntry.get())
            numbeams = int(beamsEntry.get())
            minsize = int(minEntry.get())
            maxsize = int(maxEntry.get())
            binthresh = int(threshEntry.get())
            self.create_reference.main(input,output,numbeams,minsize,maxsize,binthresh)

        def accum_inputdir_clicked():
            self.accum_inputpath = tkfd.askdirectory(initialdir='/')
            accuminputEntry.insert(tk.END, self.accum_inputpath)
            print('Select')
            print(self.accum_inputpath)

        def accum_ellipse_clicked():
            ref = Path(outputEntry.get())
            input = Path(accuminputEntry.get())
            numbeams = int(beamsEntry.get())
            self.accumulate_intensity.main(ref,input,numbeams)

        self.inputdir = tk.Button(text='Select', command=inputdir_clicked)
        self.inputdir.place(x=labelx+txtmovex+250, y=labely-10)
        self.outputdir = tk.Button(text='Select', command=outputdir_clicked)
        self.outputdir.place(x=labelx+txtmovex+250, y=labely + 20)
        self.getref_ellipse = tk.Button(text='Get Ellipse', command=getref_ellipse_clicked)
        self.getref_ellipse.place(x=labelx+200, y=labely + 120)
        self.accum_inputdir = tk.Button(text='Select', command=accum_inputdir_clicked)
        self.accum_inputdir.place(x=labelx + txtmovex + 250, y=labely+150)
        self.accum_ellipse = tk.Button(text='Accumulate intensity of ellipse', command=accum_ellipse_clicked)
        self.accum_ellipse.place(x=labelx + 200, y=labely + 170)



class Main:
    def __init__(self):
        self.gui=GUI()
        self.gui.root.mainloop()


if __name__=="__main__":
    Main()

import tkinter as tk
import tkinter.ttk as ttk
from tkinter import messagebox
import threading
import tkinter.filedialog as tkfd
from pathlib import Path
from module.create_reference import CreateReference
from module.show_infrared_camera import ShowInfraredCamera
from module.accumulate_intensity import AccumulateIntensity
from module.dnn import DNNClasifier


class GUI:
    def __init__(self):
        self.create_reference = CreateReference()
        self.accumulate_intensity = AccumulateIntensity()
        self.root=tk.Tk()
        self.nb = ttk.Notebook(width=1000, height=400)
        self.tab1 = tk.Frame(self.nb)
        self.tab2 = tk.Frame(self.nb)
        self.nb.add(self.tab1, text='カメラ')
        self.nb.add(self.tab2, text='ビーム積算')
        self.nb.pack(expand=1, fill='both')
        #self.ROOT_X = 1000
        #self.ROOT_Y = 700
        self.root.title(u"Real-time Beam Identification 2019 made by Mitsuhashi")
        #self.root.geometry(str(self.ROOT_X) + "x" + str(self.ROOT_Y))
        self.root.resizable(width=0, height=0)
        self.cameraFrame() #トリガー、ゲイン、露出、保存を決めるフレーム
        self.ellipseFrame()
        self.dnn_frame()

    def cameraFrame(self):
        configFrame = tk.LabelFrame(self.tab1,bd=2,relief="ridge",text="カメラの共通設定")
        configFrame.pack(anchor=tk.W,pady=5)
        saveFrame = tk.LabelFrame(self.tab1,bd=2,relief="ridge",text="映像保存")
        saveFrame.pack(anchor=tk.W,pady=5)
        lbl = tk.Label(configFrame,text='トリガータイプを選択してください。')
        lbl.grid(row=0,column=0)
        lbl = tk.Label(configFrame,text='ゲイン[db]を選択してください。')
        lbl.grid(row=1, column=0)
        lbl = tk.Label(configFrame,text='露出[um]を選択してください。')
        lbl.grid(row=2,column=0)
        lbl = tk.Label(saveFrame,text='保存先を選択してください。')
        lbl.grid(row=0, column=0)
        lbl = tk.Label(saveFrame,text='保存数を選択してください。')
        lbl.grid(row=1, column=0)

        # ラジオボタンのラベルをリスト化する
        self.trigger_rdo_txt = ['software', 'hardware']
        # ラジオボタンの状態
        self.trigger_rdo_var = tk.IntVar()
        # ラジオボタンを動的に作成して配置

        for i in range(len(self.trigger_rdo_txt)):
            self.trigger_rdo = tk.Radiobutton(configFrame, value=i, variable=self.trigger_rdo_var,
                                              text=self.trigger_rdo_txt[i])
            self.trigger_rdo.grid(row=0,column=i+1,sticky=tk.W)
        # ゲインのテキストボックスを出現させる
        self.gainEntry = tk.Entry(configFrame,width=20)  # widthプロパティで大きさを変える
        self.gainEntry.insert(tk.END, u'0')  # 最初から文字を入れておく
        self.gainEntry.grid(row=1, column=1)

        # 露出のテキストボックスを出現させる
        self.expEntry = tk.Entry(configFrame,width=20)  # widthプロパティで大きさを変える
        self.expEntry.insert(tk.END, u'20000')  # 最初から文字を入れておく
        self.expEntry.grid(row=2, column=1)

        # 保存先のテキストボックスを出現させる
        saveEntry = tk.Entry(saveFrame,width=70)  # widthプロパティで大きさを変える
        saveEntry.grid(row=0, column=1)

        # 保存数のテキストボックスを出現させる
        numEntry = tk.Entry(saveFrame,width=20)  # widthプロパティで大きさを変える
        numEntry.insert(tk.END, u'10')  # 最初から文字を入れておく
        numEntry.grid(row=1, column=1, sticky=tk.W)

        def button1_clicked():
            try:
                self.cvv = None
                self.cvv = ShowInfraredCamera()
                trigger_type = self.trigger_rdo_txt[self.trigger_rdo_var.get()]
                gainEntry_value = int(self.gainEntry.get())
                expEntry_value = int(self.expEntry.get())
                th = threading.Thread(target=self.cvv.show_beam, args=(trigger_type,gainEntry_value,expEntry_value))
                th.start()
            except RuntimeError:
                messagebox.showerror('connecterror','USBにカメラが接続されていません。')

        def showcolor_clicked():
            try:
                self.cvv = None
                self.cvv = ShowInfraredCamera()
                trigger_type = self.trigger_rdo_txt[self.trigger_rdo_var.get()]
                gainEntry_value = int(self.gainEntry.get())
                expEntry_value = int(self.expEntry.get())
                th = threading.Thread(target=self.cvv.show_beam_color, args=(trigger_type,gainEntry_value,expEntry_value))
                th.start()
            except RuntimeError:
                messagebox.showerror('connecterror','USBにカメラが接続されていません。')

        def selectdir_clicked():
            savepath = tkfd.askdirectory()
            saveEntry.insert(tk.END, savepath)

        def save_clicked():
            savecount = int(numEntry.get())
            try:
                if len(saveEntry.get()) == 0:
                    messagebox.showerror('patherror', '保存先フォルダが選択されていません。')

                else:
                    self.cvv.save(savecount,saveEntry.get())
                    messagebox.showinfo('Updated setting to save','カメラ画像を保存しました。（カメラが起動していない場合は保存予約になります。）')

            except AttributeError:
                messagebox.showerror('starterror', 'カメラが起動していません。')



        self.selectdir = tk.Button(saveFrame,text='Select', command=selectdir_clicked)
        self.selectdir.grid(row=0, column=2)
        self.button1 = tk.Button(saveFrame, text='表示', command=button1_clicked)
        self.button1.grid(row=2, column=2)
        self.showcolor = tk.Button(saveFrame, text='表示 (カラーマップNボタンで変更可)', command=showcolor_clicked)
        self.showcolor.grid(row=2, column=3)
        self.save = tk.Button(saveFrame,text='保存 (識別中でも使用可)', command=save_clicked)
        self.save.grid(row=2, column=4)

    def ellipseFrame(self):
        configelipseFrame = tk.LabelFrame(self.tab2, bd=2, relief="ridge", text="共通設定（下記の二つで使います。）")
        configelipseFrame.pack(anchor=tk.W,pady=5)
        ellipseparamFrame = tk.LabelFrame(self.tab2, bd=2, relief="ridge", text="ビームの形を取得")
        ellipseparamFrame.pack(anchor=tk.W,pady=5)
        accumellipseFrame = tk.LabelFrame(self.tab2, bd=2, relief="ridge", text="ビームの積算値を取得")
        accumellipseFrame.pack(anchor=tk.W,pady=5)

        lbl = tk.Label(configelipseFrame,text='ビームの本数を選択してください')
        lbl.grid(row=0, column=0, sticky=tk.W)
        lbl = tk.Label(configelipseFrame,text='ビームの形を保存するor利用するディレクトリを選択してください。')
        lbl.grid(row=1, column=0, sticky=tk.W)

        lbl = tk.Label(ellipseparamFrame,text='楕円の短軸長の最小閾値を選択してください。')
        lbl.grid(row=0, column=0, sticky=tk.W)
        lbl = tk.Label(ellipseparamFrame,text='楕円の短軸長の最大閾値を選択してください。')
        lbl.grid(row=1, column=0, sticky=tk.W)
        lbl = tk.Label(ellipseparamFrame,text='二値化の閾値 (0の場合，Otsus methodが使われる)を選択してください。')
        lbl.grid(row=2, column=0, sticky=tk.W)
        lbl = tk.Label(ellipseparamFrame,text='リファレンス画像を保存したディレクトリを選択してください。')
        lbl.grid(row=3, column=0, sticky=tk.W)

        lbl = tk.Label(accumellipseFrame,text='積算したいビーム画像を格納したディレクトリを選択してください。')
        lbl.grid(row=0, column=0, sticky=tk.W)
        lbl = tk.Label(accumellipseFrame,text='積算データを保存するディレクトリを選択してください。')
        lbl.grid(row=1, column=0, sticky=tk.W)

        # テキストボックス
        beamsEntry = tk.Entry(configelipseFrame, width=10)  # widthプロパティで大きさを変える
        beamsEntry.insert(tk.END, u'3')  # 最初から文字を入れておく
        beamsEntry.grid(row=0, column=1, sticky=tk.W)
        outputEntry = tk.Entry(configelipseFrame, width=40)  # widthプロパティで大きさを変える
        outputEntry.grid(row=1, column=1, sticky=tk.W)

        minEntry = tk.Entry(ellipseparamFrame, width=10)  # widthプロパティで大きさを変える
        minEntry.insert(tk.END, u'100')  # 最初から文字を入れておく
        minEntry.grid(row=0, column=1, sticky=tk.W)
        maxEntry = tk.Entry(ellipseparamFrame, width=10)  # widthプロパティで大きさを変える
        maxEntry.insert(tk.END, u'10000')  # 最初から文字を入れておく
        maxEntry.grid(row=1, column=1, sticky=tk.W)
        threshEntry = tk.Entry(ellipseparamFrame, width=10)  # widthプロパティで大きさを変える
        threshEntry.insert(tk.END, u'0')  # 最初から文字を入れておく
        threshEntry.grid(row=2, column=1, sticky=tk.W)
        inputEntry = tk.Entry(ellipseparamFrame,width=40)  # widthプロパティで大きさを変える
        inputEntry.grid(row=3, column=1, sticky=tk.W)


        accuminputEntry = tk.Entry(accumellipseFrame,width=40)  # widthプロパティで大きさを変える
        accuminputEntry.grid(row=0,column=1, sticky=tk.W)
        accumoutputEntry = tk.Entry(accumellipseFrame,width=40)  # widthプロパティで大きさを変える
        accumoutputEntry.grid(row=1, column=1, sticky=tk.W)

        def inputdir_clicked():
            self.inputpath = tkfd.askdirectory()
            inputEntry.insert(tk.END, self.inputpath)

        def outputdir_clicked():
            self.outputpath = tkfd.askdirectory()
            outputEntry.insert(tk.END, self.outputpath)

        def getref_ellipse_clicked():
            input = Path(inputEntry.get())
            output = Path(outputEntry.get())
            numbeams = int(beamsEntry.get())
            minsize = int(minEntry.get())
            maxsize = int(maxEntry.get())
            binthresh = int(threshEntry.get())
            self.create_reference.main(input,output,numbeams,minsize,maxsize,binthresh)

        def accum_inputdir_clicked():
            self.accum_inputpath = tkfd.askdirectory()
            accuminputEntry.insert(tk.END, self.accum_inputpath)


        def accum_outputdir_clicked():
            self.accum_outputpath = tkfd.askdirectory()
            accumoutputEntry.insert(tk.END, self.accum_outputpath)


        def accum_ellipse_clicked():
            ref = Path(outputEntry.get())
            input = Path(accuminputEntry.get())
            output = accumoutputEntry.get()
            numbeams = int(beamsEntry.get())
            self.accumulate_intensity.main(ref,input,output,numbeams)

        self.outputdir = tk.Button(configelipseFrame,text='Select', command=outputdir_clicked)
        self.outputdir.grid(row=1,column=2, sticky=tk.W)

        self.inputdir = tk.Button(ellipseparamFrame,text='Select', command=inputdir_clicked)
        self.inputdir.grid(row=3,column=2, sticky=tk.W)
        self.getref_ellipse = tk.Button(ellipseparamFrame,text='Get Ellipse', command=getref_ellipse_clicked)
        self.getref_ellipse.grid(row=4,column=2, sticky=tk.W,pady=5)

        self.accum_inputdir = tk.Button(accumellipseFrame,text='Select', command=accum_inputdir_clicked)
        self.accum_inputdir.grid(row=0,column=2, sticky=tk.W)
        self.accum_outputdir = tk.Button(accumellipseFrame,text='Select', command=accum_outputdir_clicked)
        self.accum_outputdir.grid(row=1,column=2, sticky=tk.W)
        self.accum_ellipse = tk.Button(accumellipseFrame,text='Accumulate intensity of ellipse', command=accum_ellipse_clicked)
        self.accum_ellipse.grid(row=2,column=2, sticky=tk.W,pady=5)

    def dnn_frame(self):
        dnnFrame = tk.LabelFrame(self.tab1, width=600,height=200,bd=2, relief="ridge",
                                          text="Deep Learning (Supervised Learning)")
        dnnFrame.pack(anchor=tk.W,pady=5)

        lbl = tk.Label(dnnFrame,text='ビームの数or画像')
        lbl.grid(row=0, column=0,sticky=tk.W,pady=2)
        lbl = tk.Label(dnnFrame,text='訓練(train)フォルダ')
        lbl.grid(row=1, column=0,sticky=tk.W)
        lbl = tk.Label(dnnFrame,text='検証(validation)フォルダ (任意)')
        lbl.grid(row=2, column=0,sticky=tk.W)

        # テキストボックス
        trainEntry = tk.Entry(dnnFrame,width=70)  # widthプロパティで大きさを変える
        trainEntry.insert(tk.END,u'C:/Users/ryoya/PycharmProjects/terahertz-image-tools/sample/train')
        trainEntry.grid(row=1,column=1,sticky=tk.W)
        valEntry = tk.Entry(dnnFrame,width=70)  # widthプロパティで大きさを変える
        valEntry.grid(row=2,column=1,sticky=tk.W)

        # ラジオボタンのラベルをリスト化する
        rdo_txt = ['image','1', '2', '3', '4', '5', '6', '7', '8', '9 ', '10']
        # ラジオボタンの状態
        rdo_var = tk.IntVar()
        # ラジオボタンを動的に作成して配置
        for i in range(len(rdo_txt)):
            rdo = tk.Radiobutton(dnnFrame, value=i, variable=rdo_var, text=rdo_txt[i])
            rdo.place(relx=0.12+0.07*i,rely=0)


        def trainfolderbutton_clicked():
            trainpath = tkfd.askdirectory(title='訓練(train)フォルダを選択してください')
            trainEntry.insert(tk.END, trainpath)

        def valfolderbutton_clicked():
            valpath = tkfd.askdirectory(title='検証(val)フォルダを選択してください')
            valEntry.insert(tk.END, valpath)

        def status_clicked():
            active = threading.enumerate()
            if len(active) == 1:
                self.trainbutton.config(text='訓練', state='active')
                messagebox.showinfo('status', '更新しました')
            else:
                messagebox.showinfo('status','訓練中です。')

        def dnn_train_clicked():

            if len(trainEntry.get()) == 0:
                messagebox.showerror('エラー','訓練フォルダが選択されていません。')
            else:
                imtype = rdo_txt[rdo_var.get()]
                if imtype == 'image':
                    self.trainbutton.config(text="訓練中",state="disable")
                    dnn_classifier = DNNClasifier(imtype,trainEntry.get(),valEntry.get())
                    th = threading.Thread(target=dnn_classifier.train)#dnn_classifier.train()のように書くとフリーズします！
                    th.start()
                else:
                    messagebox.showerror('selecterror','現在ビームの積算の値を用いた識別は実装されていません。imageを選択してください。')

        def dnn_test_clicked():
            try:
                self.cvv = ShowInfraredCamera()
                self.cvv = None
                imtype = rdo_txt[rdo_var.get()]
                if imtype == 'image':
                    trigger_type = self.trigger_rdo_txt[self.trigger_rdo_var.get()]
                    gainEntry_value = int(self.gainEntry.get())
                    expEntry_value = int(self.expEntry.get())
                    dnn_classifier = DNNClasifier(imtype, trainEntry.get(), valEntry.get())
                    th = threading.Thread(target=dnn_classifier.test, args=(trigger_type,gainEntry_value,expEntry_value))
                    th.start()
                else:
                    messagebox.showerror('selecterror', '現在ビームの積算の値を用いた識別は実装されていません。imageを選択してください。')

            except RuntimeError:
                messagebox.showerror('connecterror','USBにカメラが接続されていません。')

        def dnn_test_color_clicked():
            try:
                self.cvv = ShowInfraredCamera()
                self.cvv = None
                imtype = rdo_txt[rdo_var.get()]
                if imtype == 'image':
                    trigger_type = self.trigger_rdo_txt[self.trigger_rdo_var.get()]
                    gainEntry_value = int(self.gainEntry.get())
                    expEntry_value = int(self.expEntry.get())
                    dnn_classifier = DNNClasifier(imtype, trainEntry.get(), valEntry.get())
                    th = threading.Thread(target=dnn_classifier.test_color, args=(trigger_type,gainEntry_value,expEntry_value))
                    th.start()
                else:
                    messagebox.showerror('selecterror', '現在ビームの積算の値を用いた識別は実装されていません。imageを選択してください。')

            except RuntimeError:
                messagebox.showerror('connecterror','USBにカメラが接続されていません。')

        self.trainfolderbutton = tk.Button(dnnFrame,text='Select', command=trainfolderbutton_clicked)
        self.trainfolderbutton.grid(row=1,column=2)
        self.valfolderbutton = tk.Button(dnnFrame,text='Select', command=valfolderbutton_clicked)
        self.valfolderbutton.grid(row=2,column=2)
        self.trainbutton = tk.Button(dnnFrame,text='Train', command=dnn_train_clicked)
        self.trainbutton.grid(row=6,column=2)
        self.statusbutton = tk.Button(dnnFrame,text='Update status', command=status_clicked)
        self.statusbutton.grid(row=6,column=3)
        self.testbutton = tk.Button(dnnFrame,text='Realtime-Predict', command=dnn_test_clicked)
        self.testbutton.grid(row=6,column=4)
        self.testcolorbutton = tk.Button(dnnFrame, text='Realtime-Predict (カラーマップ)', command=dnn_test_color_clicked)
        self.testcolorbutton.grid(row=7, column=4)


class Main:
    def __init__(self):
        self.gui=GUI()
        self.gui.root.mainloop()


if __name__=="__main__":
    Main()

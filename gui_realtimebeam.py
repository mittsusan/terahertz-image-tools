import tkinter as tk
from tkinter import messagebox
import threading
import tkinter.filedialog as tkfd
from pathlib import Path
from module.create_reference import CreateReference
from module.show_infrared_camera import ShowInfraredCamera
from module.accumulate_intensity import AccumulateIntensity
from module.dnn import DNNClasifier
#from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
#from concurrent.futures import ThreadPoolExecutor

class GUI:
    def __init__(self):
        self.create_reference = CreateReference()
        self.accumulate_intensity = AccumulateIntensity()
        self.root=tk.Tk()
        self.ROOT_X = 1300
        self.ROOT_Y = 850
        self.CANVAS_X=640
        self.CANVAS_Y=480
        self.root.title(u"Real-time Beam Identification 2019 made by Mitsuhashi")
        self.root.geometry(str(self.ROOT_X) + "x" + str(self.ROOT_Y))
        self.root.resizable(width=0, height=0)
        self.firstFrame() #トリガー、ゲイン、露出、保存を決めるフレーム
        self.ellipseFrame()
        self.dnn_frame()

    def firstFrame(self):
        # ラベル
        labelx = 30

        lbl = tk.Label(text='トリガータイプを選択してください。')
        lbl.place(x=labelx, y=30)
        lbl = tk.Label(text='ゲイン[db]を選択してください。')
        lbl.place(x=labelx, y=70)
        lbl = tk.Label(text='露出[um]を選択してください。')
        lbl.place(x=labelx, y=90)
        lbl = tk.Label(text='保存先を選択してください。')
        lbl.place(x=400, y=30)
        lbl = tk.Label(text='保存数を選択してください。')
        lbl.place(x=400, y=60)

        # ラジオボタンのラベルをリスト化する
        self.trigger_rdo_txt = ['software', 'hardware']
        # ラジオボタンの状態
        self.trigger_rdo_var = tk.IntVar()
        # ラジオボタンを動的に作成して配置
        for i in range(len(self.trigger_rdo_txt)):
            self.trigger_rdo = tk.Radiobutton(self.root, value=i, variable=self.trigger_rdo_var,
                                              text=self.trigger_rdo_txt[i])
            self.trigger_rdo.place(x=200, y=15 + (i * 24))

        # ゲインのテキストボックスを出現させる
        self.gainEntry = tk.Entry(width=20)  # widthプロパティで大きさを変える
        self.gainEntry.insert(tk.END, u'0')  # 最初から文字を入れておく
        self.gainEntry.place(x=200, y=70)

        # 露出のテキストボックスを出現させる
        self.expEntry = tk.Entry(width=20)  # widthプロパティで大きさを変える
        self.expEntry.insert(tk.END, u'20000')  # 最初から文字を入れておく
        self.expEntry.place(x=200, y=90)

        # 保存先のテキストボックスを出現させる
        saveEntry = tk.Entry(width=40)  # widthプロパティで大きさを変える
        saveEntry.place(x=550, y=30)

        # 保存数のテキストボックスを出現させる
        numEntry = tk.Entry(width=20)  # widthプロパティで大きさを変える
        numEntry.insert(tk.END, u'10')  # 最初から文字を入れておく
        numEntry.place(x=550, y=60)

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

        self.button1 = tk.Button(text='OK',command=button1_clicked)
        self.button1.place(x=50, y=110)

        self.selectdir = tk.Button(text='Select', command=selectdir_clicked)
        self.selectdir.place(x=800, y=25)

        self.save = tk.Button(text='Save', command=save_clicked)
        self.save.place(x=480, y=80)

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
        lbl = tk.Label(text='積算データを保存するディレクトリを選択してください。')
        lbl.place(x=labelx, y=labely + 170)

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
        accumoutputEntry = tk.Entry(width=40)  # widthプロパティで大きさを変える
        accumoutputEntry.place(x=labelx + txtmovex, y=labely + 170)

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

        self.inputdir = tk.Button(text='Select', command=inputdir_clicked)
        self.inputdir.place(x=labelx+txtmovex+250, y=labely-10)
        self.outputdir = tk.Button(text='Select', command=outputdir_clicked)
        self.outputdir.place(x=labelx+txtmovex+250, y=labely + 20)
        self.getref_ellipse = tk.Button(text='Get Ellipse', command=getref_ellipse_clicked)
        self.getref_ellipse.place(x=labelx+200, y=labely + 120)
        self.accum_inputdir = tk.Button(text='Select', command=accum_inputdir_clicked)
        self.accum_inputdir.place(x=labelx + txtmovex + 250, y=labely+140)
        self.accum_outputdir = tk.Button(text='Select', command=accum_outputdir_clicked)
        self.accum_outputdir.place(x=labelx + txtmovex + 250, y=labely + 170)
        self.accum_ellipse = tk.Button(text='Accumulate intensity of ellipse', command=accum_ellipse_clicked)
        self.accum_ellipse.place(x=labelx + 200, y=labely + 190)

    def dnn_frame(self):
        # ラベル
        labelx = 30
        labely = 500
        txtmovex = 150
        lbl = tk.Label(text='クラス数を選択してください。')
        lbl.place(x=labelx, y=labely)
        lbl = tk.Label(text='クラス名を半角カンマ区切りで入力してください。（入力順は0,1,,,9,,,,a,b,c,,,の順番に入力してください。）')
        lbl.place(x=labelx, y=labely+50)
        lbl = tk.Label(text='訓練(train)フォルダ')
        lbl.place(x=labelx + 300, y=labely - 20)
        lbl = tk.Label(text='検証(validation)フォルダ')
        lbl.place(x=labelx + 600, y=labely - 20)
        lbl = tk.Label(text='ビームの数or画像')
        lbl.place(x=labelx + 870, y=labely - 20)
        # テキストボックスw
        classEntry = tk.Entry(width=10)  # widthプロパティで大きさを変える
        classEntry.insert(tk.END, u'4')  # 最初から文字を入れておく
        classEntry.place(x=labelx + txtmovex, y=labely)
        trainEntry = tk.Entry(width=40)  # widthプロパティで大きさを変える
        trainEntry.insert(tk.END,u'C:/Users/ryoya/PycharmProjects/terahertz-image-tools/sample/train')
        trainEntry.place(x=300, y=labely)
        valEntry = tk.Entry(width=40)  # widthプロパティで大きさを変える
        valEntry.insert(tk.END, u'C:/Users/ryoya/PycharmProjects/terahertz-image-tools/sample/validation')
        valEntry.place(x=600, y=labely)
        classnameEntry = tk.Entry(width=50)
        classnameEntry.insert(tk.END,u'None,Si0.05,Si0.10,Si0.20')
        classnameEntry.place(x=labelx, y=labely + 70)

        # ラジオボタンのラベルをリスト化する
        rdo_txt = ['image','1', '2', '3', '4', '5', '6', '7', '8', '9 ', '10']
        # ラジオボタンの状態
        rdo_var = tk.IntVar()
        # ラジオボタンを動的に作成して配置
        for i in range(6):
            rdo = tk.Radiobutton(self.root, value=i, variable=rdo_var, text=rdo_txt[i])
            rdo.place(x=900, y=labely+ (i * 24))
        for i in range(6,len(rdo_txt)):
            rdo = tk.Radiobutton(self.root, value=i, variable=rdo_var, text=rdo_txt[i])
            rdo.place(x=980, y=labely+ ((i-6) * 24))

        '''
        フォルダを分割して選択する場合
        def class_clicked():
            classcount = int(classEntry.get())
            self.trainbutton.config(state='active')
            for index in range(classcount):
                # execは""で書かないとstrが打ち込めない！！
                exec('classnum%d = tk.Entry(width=10)' % (index))
                exec('classnum%d.place(x=%d+300, y=450 + %d*20)' % (index, labelx, index))
                exec('classtraindir%d = tk.Entry(width=40)' % (index))
                exec('classtraindir%d.place(x=%d+400, y=450 + %d*20)' % (index, labelx, index))
                exec('classvaldir%d = tk.Entry(wi dth=40)' % (index))
                exec('classvaldir%d.place(x=%d+650, y=450 + %d*20)' % (index, labelx, index))
                exec("classtrainpath%d = tkfd.askdirectory(title='訓練(train)フォルダを選択してください')" % (index))
                exec('classtraindir%d.insert(tk.END, classtrainpath%d)' % (index, index))
                exec("classvalpath%d = tkfd.askdirectory(title='検証(val)フォルダを選択してください')" % (index))
                exec('classvaldir%d.insert(tk.END, classvalpath%d)' % (index, index))
                print('Select')
    
            ボタン形式下記作成途中
            def classtrainbutton_clicked(index):
                exec("classtrainpath{} = tkfd.askdirectory(title='訓練(train)フォルダを選択してください')".format(index))
                exec("classtraindir{0}.insert(tk.END, classtrainpath{0})".format(index))

            def classvalbutton_clicked(index):
                exec("classvalpath%d = tkfd.askdirectory(title='検証(val)フォルダを選択してください')" % (index))
                exec('classvaldir%d.insert(tk.END, classvalpath%d)' % (index, index))

            for index in range(classcount):
                #execは""で書かないとstrが打ち込めない！！
                exec('classnum{} = tk.Entry(width=10)'.format(index))
                exec('classnum%d.place(x=%d+300, y=450 + %d*20)'%(index,labelx,index))
                exec('classtraindir%d = tk.Entry(width=40)' % (index))
                exec('classtraindir%d.place(x=%d+400, y=450 + %d*20)' % (index, labelx, index))
                exec('classvaldir%d = tk.Entry(width=40)' % (index))
                exec('classvaldir%d.place(x=%d+700, y=450 + %d*20)' % (index, labelx, index))
                exec("classtrainbutton%d = tk.Button(text='Select', command=lambda: classtrainbutton_clicked(%d))"%(index,index))
                exec("classtrainbutton{0}.place(x={1}+600, y=440 + {0}*25)".format(index,labelx))
                #classtrainbutton = tk.Button(text='Select', command=lambda: classtrainbutton_clicked(index))
                #classtrainbutton.place(x=labelx+600, y=440 + index*25)
            '''


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
            if len(trainEntry.get()) + len(valEntry.get()) == 0:
                messagebox.showerror('エラー','訓練or検証フォルダが選択されていません。')
            else:
                self.trainbutton.config(text="訓練中",state="disable")
                classcount = int(classEntry.get())
                imtype = rdo_txt[rdo_var.get()]

                '''
                traindirlist = []
                valdirlist = []
                for index in range(classcount):
                    exec("traindirlist.append(classtraindir%d)"%(index))
                    exec("valdirlist.append(classvaldir%d)" % (index))
                print(traindirlist)
                DNNClasifier(traindirlist,valdirlist,classcount)
                '''
                dnn_classifier = DNNClasifier(imtype,trainEntry.get(),valEntry.get(),classcount)
                th = threading.Thread(target=dnn_classifier.train)#dnn_classifier.train()のように書くとフリーズします！
                th.start()

        def dnn_test_clicked():
            try:
                self.cvv = ShowInfraredCamera()
                self.cvv = None
                classcount = int(classEntry.get())
                classnamelist = sorted(classnameEntry.get().split(','))
                print('sorted:classname{}'.format(classnamelist))
                if len(classnamelist) == classcount:
                    trigger_type = self.trigger_rdo_txt[self.trigger_rdo_var.get()]
                    gainEntry_value = int(self.gainEntry.get())
                    expEntry_value = int(self.expEntry.get())
                    imtype = rdo_txt[rdo_var.get()]
                    dnn_classifier = DNNClasifier(imtype, trainEntry.get(), valEntry.get(), classcount)
                    th = threading.Thread(target=dnn_classifier.test, args=(trigger_type,gainEntry_value,expEntry_value,classnamelist))
                    th.start()
                else:
                    messagebox.showerror('classnameerror','クラス名の数とクラス数が一致していません。')

            except RuntimeError:
                messagebox.showerror('connecterror','USBにカメラが接続されていません。')
        self.trainbutton = tk.Button(text='Train', command=dnn_train_clicked)
        self.trainbutton.place(x=labelx+1000, y=labely)

        self.testbutton = tk.Button(text='Realtime-Predict', command=dnn_test_clicked)
        self.testbutton.place(x=labelx+150, y=labely+100)

        self.statusbutton = tk.Button(text='Update status', command=status_clicked)
        self.statusbutton.place(x=labelx + 1100, y=labely)

        self.trainfolderbutton= tk.Button(text='Select', command=trainfolderbutton_clicked)
        self.trainfolderbutton.place(x=labelx + 520, y=labely)

        self.valfolderbutton = tk.Button(text='Select', command=valfolderbutton_clicked)
        self.valfolderbutton.place(x=labelx + 820, y=labely)



class Main:
    def __init__(self):
        self.gui=GUI()
        self.gui.root.mainloop()


if __name__=="__main__":
    Main()

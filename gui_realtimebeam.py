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
from module.arrange_value import ArrangeValue
from module.fwhm import FWHM


class GUI:
    def __init__(self):
        self.cvv = None
        self.create_reference = CreateReference()
        self.accumulate_intensity = AccumulateIntensity()
        self.root = tk.Tk()
        self.iconfile = Path('icon/favicon.ico')
        self.root.iconbitmap(default=self.iconfile)
        self.nb = ttk.Notebook(width=1040, height=530)
        self.tab1 = tk.Frame(self.nb)
        self.tab2 = tk.Frame(self.nb)
        self.nb.add(self.tab1, text='近赤外カメラ (リアルタイム)')
        self.nb.add(self.tab2, text='ビーム画像積算 (グレースケール画像のみ対応)')
        self.nb.pack(expand=1, fill='both')
        self.root.title(u"Real-time Beam Identification 2019 made by Mitsuhashi")
        self.root.resizable(width=0, height=0)
        self.cameraFrame() #トリガー、ゲイン、露出、保存を決めるフレーム
        self.ellipseFrame()
        self.dnn_frame()
        self.normflag = False
    def cameraFrame(self):
        configFrame = tk.LabelFrame(self.tab1,bd=2,relief="ridge",text="カメラの共通設定")
        configFrame.pack(anchor=tk.W,pady=5)
        saveFrame = tk.LabelFrame(self.tab1,bd=2,relief="ridge",text="映像保存")
        saveFrame.pack(anchor=tk.W,pady=5)
        profilerFrame = tk.LabelFrame(self.tab1, bd=2, relief="ridge", text="ビームプロファイラ")
        profilerFrame.pack(anchor=tk.W, pady=5)

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
        lbl = tk.Label(saveFrame, text='～～～～録画設定～～～～')
        lbl.grid(row=2, column=0)
        lbl = tk.Label(saveFrame, text='フレームレートを入力してください。 (fps=Hz)')
        lbl.grid(row=3, column=0)
        lbl = tk.Label(saveFrame, text='高さを入力してください。 (pix)')
        lbl.grid(row=4, column=0)
        lbl = tk.Label(saveFrame, text='幅を入力してください。 (pix)')
        lbl.grid(row=5, column=0)

        lbl = tk.Label(profilerFrame, text='ビームの本数を選択してください')
        lbl.grid(row=0, column=0, sticky=tk.W)
        lbl = tk.Label(profilerFrame,
                       text='楕円の短軸長(pix)の最小閾値を選択してください。この値より小さいビームは検出されません。(全体を2048pix×2048pixとして考える)')
        lbl.grid(row=1, column=0, sticky=tk.W)
        lbl = tk.Label(profilerFrame,
                       text='楕円の短軸長(pix)の最大閾値を選択してください。この値より大きいビームは検出されません。(全体を2048pix×2048pixとして考える)')
        lbl.grid(row=2, column=0, sticky=tk.W)
        lbl = tk.Label(profilerFrame,
                       text='二値化の閾値 (0の場合，大津の二値化が使われる)を選択してください。(0～255の間) (ビーム強度が弱いと大津の二値化を使わないとビーム検出が上手く出来ません。)')
        lbl.grid(row=3, column=0, sticky=tk.W)


        # ラジオボタンのラベルをリスト化する
        self.trigger_rdo_txt = ['software', 'hardware']
        # ラジオボタンの状態
        self.trigger_rdo_var = tk.IntVar()
        # ラジオボタンを動的に作成して配置
        # value=1のラジオボタンにチェックを入れる
        self.trigger_rdo_var.set(1)
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
        self.expEntry.insert(tk.END, u'30000')  # 最初から文字を入れておく
        self.expEntry.grid(row=2, column=1)
        # 保存先のテキストボックスを出現させる
        saveEntry = tk.Entry(saveFrame,width=80)  # widthプロパティで大きさを変える
        saveEntry.grid(row=0, column=1)
        # 保存数のテキストボックスを出現させる
        numEntry = tk.Entry(saveFrame,width=20)  # widthプロパティで大きさを変える
        numEntry.insert(tk.END, u'10')  # 最初から文字を入れておく
        numEntry.grid(row=1, column=1, sticky=tk.W)
        fpsEntry = tk.Entry(saveFrame, width=20)  # widthプロパティで大きさを変える
        fpsEntry.insert(tk.END, u'10')  # 最初から文字を入れておく
        fpsEntry.grid(row=3, column=1, sticky=tk.W)
        heightEntry = tk.Entry(saveFrame, width=20)  # widthプロパティで大きさを変える
        heightEntry.insert(tk.END, u'2048')  # 最初から文字を入れておく
        heightEntry.grid(row=4, column=1, sticky=tk.W)
        widthEntry = tk.Entry(saveFrame, width=20)  # widthプロパティで大きさを変える
        widthEntry.insert(tk.END, u'2048')  # 最初から文字を入れておく
        widthEntry.grid(row=5, column=1, sticky=tk.W)

        beamsEntry = tk.Entry(profilerFrame, width=10)  # widthプロパティで大きさを変える
        beamsEntry.insert(tk.END, u'1')  # 最初から文字を入れておく
        beamsEntry.grid(row=0, column=1, sticky=tk.W)
        minEntry = tk.Entry(profilerFrame, width=10)  # widthプロパティで大きさを変える
        minEntry.insert(tk.END, u'100')  # 最初から文字を入れておく
        minEntry.grid(row=1, column=1, sticky=tk.W)
        maxEntry = tk.Entry(profilerFrame, width=10)  # widthプロパティで大きさを変える
        maxEntry.insert(tk.END, u'2000')  # 最初から文字を入れておく
        maxEntry.grid(row=2, column=1, sticky=tk.W)
        threshEntry = tk.Entry(profilerFrame, width=10)  # widthプロパティで大きさを変える
        threshEntry.insert(tk.END, u'0')  # 最初から文字を入れておく
        threshEntry.grid(row=3, column=1, sticky=tk.W)


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

        def select_cleardir_clicked():
            saveEntry.delete(0,tk.END)

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

        def video_finish_clicked():
            self.cvv.video_finish()
            self.video_save.config(text='録画', command=video_save_clicked)

        def color_video_finish_clicked():
            self.cvv.video_finish()
            self.video_save.config(text='録画(カラー)', command=color_video_save_clicked)

        def video_save_clicked():
            try:
                if len(saveEntry.get()) == 0:
                    messagebox.showerror('patherror', '保存先フォルダが選択されていません。')

                else:
                    self.cvv.video_save(saveEntry.get(), float(fpsEntry.get()), int(heightEntry.get()),
                                        int(widthEntry.get()), False)
                    self.video_save.config(text='終了', command=video_finish_clicked)
            except AttributeError:
                messagebox.showerror('starterror', 'カメラが起動していません。')

        def color_video_save_clicked():
            try:
                if len(saveEntry.get()) == 0:
                    messagebox.showerror('patherror', '保存先フォルダが選択されていません。')

                else:
                    self.cvv.video_save(saveEntry.get(), float(fpsEntry.get()), int(heightEntry.get()),
                                        int(widthEntry.get()), True)
                    self.video_save.config(text='終了', command=color_video_finish_clicked)
            except AttributeError:
                messagebox.showerror('starterror', 'カメラが起動していません。')

        def norm_clicked():
            try:
                if self.normflag == False:
                    self.cvv.min_max_flag()
                    print('min-max-normalization')
                    self.norm.config(text='元に戻す')
                    self.normflag = True
                else:
                    self.cvv.min_max_flag()
                    print('元に戻しました')
                    self.norm.config(text='min-max-normalization')
                    self.normflag = False
            except AttributeError:
                messagebox.showerror('starterror', 'カメラが起動していません。')

        def profiler_button_clicked():
            try:
                self.cvv = None
                self.cvv = ShowInfraredCamera()
                trigger_type = self.trigger_rdo_txt[self.trigger_rdo_var.get()]
                gainEntry_value = int(self.gainEntry.get())
                expEntry_value = int(self.expEntry.get())
                th = threading.Thread(target=self.cvv.beam_profiler, args=(trigger_type, gainEntry_value, expEntry_value))
                th.start()
            except RuntimeError:
                messagebox.showerror('connecterror', 'USBにカメラが接続されていません。')

        def profiler_color_button_clicked():
            try:
                self.cvv = None
                self.cvv = ShowInfraredCamera()
                trigger_type = self.trigger_rdo_txt[self.trigger_rdo_var.get()]
                gainEntry_value = int(self.gainEntry.get())
                expEntry_value = int(self.expEntry.get())
                th = threading.Thread(target=self.cvv.beam_profiler_color, args=(
                trigger_type, gainEntry_value, expEntry_value))
                th.start()
            except RuntimeError:
                messagebox.showerror('connecterror', 'USBにカメラが接続されていません。')

        def detectellipse_button_clicked():
            try:
                numbeams = int(beamsEntry.get())
                minsize = int(minEntry.get())
                maxsize = int(maxEntry.get())
                binthresh = int(threshEntry.get())
                self.cvv.detect_ellipse(numbeams, minsize, maxsize, binthresh)

            except AttributeError:
                messagebox.showerror('starterror', 'カメラが起動していません。')

        self.profiler_button = tk.Button(configFrame, text='表示', command=profiler_button_clicked)
        self.profiler_button.grid(row=3, column=2)
        self.profiler_color_button = tk.Button(configFrame, text='カラー表示(Nボタンで色変更)', command=profiler_color_button_clicked)
        self.profiler_color_button.grid(row=3, column=3)
        self.norm = tk.Button(configFrame, text='正規化 (5fps程度)', command=norm_clicked)
        self.norm.grid(row=3, column=4)

        self.selectdir = tk.Button(saveFrame,text='Select', command=selectdir_clicked)
        self.selectdir.grid(row=0, column=2)
        self.select_cleardir = tk.Button(saveFrame, text='Clear', command=select_cleardir_clicked)
        self.select_cleardir.grid(row=0, column=3)
        '''
        self.button1 = tk.Button(saveFrame, text='表示', command=button1_clicked)
        self.button1.grid(row=2, column=0)
        self.showcolor = tk.Button(saveFrame, text='表示 (カラーNボタンで変更可)', command=showcolor_clicked)
        self.showcolor.grid(row=2, column=1)
        '''
        self.save = tk.Button(saveFrame,text='画像として保存', command=save_clicked)
        self.save.grid(row=1, column=3)

        self.video_save = tk.Button(saveFrame, text='録画 ', command=video_save_clicked)
        self.video_save.grid(row=5, column=2)
        self.video_save = tk.Button(saveFrame, text='録画(カラー) ', command=color_video_save_clicked)
        self.video_save.grid(row=5, column=3)

        self.detectellipse_button = tk.Button(profilerFrame, text='ビーム検出', command=detectellipse_button_clicked)
        self.detectellipse_button.grid(row=3, column=2)

    def ellipseFrame(self):
        configelipseFrame = tk.LabelFrame(self.tab2, bd=2, relief="ridge", text="共通設定")
        configelipseFrame.pack(anchor=tk.W,pady=5)
        ellipseparamFrame = tk.LabelFrame(self.tab2, bd=2, relief="ridge", text="ビームの形を取得")
        ellipseparamFrame.pack(anchor=tk.W,pady=5)
        accumellipseFrame = tk.LabelFrame(self.tab2, bd=2, relief="ridge", text="ビームの積算値を取得")
        accumellipseFrame.pack(anchor=tk.W,pady=5)
        fwhmFrame = tk.LabelFrame(self.tab2, bd=2, relief="ridge", text="ビームのパラメータを取得(単位mm)")
        fwhmFrame.pack(anchor=tk.W, pady=5)

        lbl = tk.Label(configelipseFrame,text='ビームの本数を選択してください')
        lbl.grid(row=0, column=0, sticky=tk.W)
        lbl = tk.Label(configelipseFrame, text='積算したいビーム画像を格納したディレクトリを選択してください。')
        lbl.grid(row=1, column=0, sticky=tk.W)
        lbl = tk.Label(configelipseFrame, text='ビームの形を保存するor利用するディレクトリを選択してください。')
        lbl.grid(row=2, column=0, sticky=tk.W)


        lbl = tk.Label(ellipseparamFrame,text='楕円の短軸長(pix)の最小閾値を選択してください。この値より小さいビームは検出されません。(全体を2048pix×2048pixとして考える)')
        lbl.grid(row=0, column=0, sticky=tk.W)
        lbl = tk.Label(ellipseparamFrame,text='楕円の短軸長(pix)の最大閾値を選択してください。この値より大きいビームは検出されません。(全体を2048pix×2048pixとして考える)')
        lbl.grid(row=1, column=0, sticky=tk.W)
        lbl = tk.Label(ellipseparamFrame,text='二値化の閾値 (0の場合，大津の二値化が使われる)を選択してください。(0～255の間) (ビーム強度が弱いと大津の二値化を使わないとビーム検出が上手く出来ません。)')
        lbl.grid(row=2, column=0, sticky=tk.W)


        lbl = tk.Label(accumellipseFrame, text='積算データ(txt)を保存するディレクトリを選択してください。')
        lbl.grid(row=0, column=0, sticky=tk.W)


        lbl = tk.Label(fwhmFrame, text='ビームの短軸、長軸、短軸FWHM、長軸FWHMを保存するディレクトリを選択してください。')
        lbl.grid(row=0, column=0, sticky=tk.W)

        # テキストボックス
        beamsEntry = tk.Entry(configelipseFrame, width=10)  # widthプロパティで大きさを変える
        beamsEntry.insert(tk.END, u'2')  # 最初から文字を入れておく
        beamsEntry.grid(row=0, column=1, sticky=tk.W)
        accuminputEntry = tk.Entry(configelipseFrame, width=80)  # widthプロパティで大きさを変える
        #accuminputEntry.insert(tk.END, u'C:/Users/ryoya/PycharmProjects/terahertz-image-tools/りえっくす/img')
        accuminputEntry.grid(row=1, column=1, sticky=tk.W)
        outputEntry = tk.Entry(configelipseFrame, width=80)  # widthプロパティで大きさを変える
        #outputEntry.insert(tk.END, u'C:/Users/ryoya/PycharmProjects/terahertz-image-tools/りえっくす/beamform')
        outputEntry.grid(row=2, column=1, sticky=tk.W)


        minEntry = tk.Entry(ellipseparamFrame, width=10)  # widthプロパティで大きさを変える
        minEntry.insert(tk.END, u'100')  # 最初から文字を入れておく
        minEntry.grid(row=0, column=1, sticky=tk.W)
        maxEntry = tk.Entry(ellipseparamFrame, width=10)  # widthプロパティで大きさを変える
        maxEntry.insert(tk.END, u'2000')  # 最初から文字を入れておく
        maxEntry.grid(row=1, column=1, sticky=tk.W)
        threshEntry = tk.Entry(ellipseparamFrame, width=10)  # widthプロパティで大きさを変える
        threshEntry.insert(tk.END, u'0')  # 最初から文字を入れておく
        threshEntry.grid(row=2, column=1, sticky=tk.W)

        accumoutputEntry = tk.Entry(accumellipseFrame,width=80)  # widthプロパティで大きさを変える
        accumoutputEntry.grid(row=0, column=1, sticky=tk.W)

        fwhmoutputEntry = tk.Entry(fwhmFrame, width=80)  # widthプロパティで大きさを変える
        #fwhmoutputEntry.insert(tk.END, u'C:/Users/ryoya/PycharmProjects/terahertz-image-tools/りえっくす/fwhm')
        fwhmoutputEntry.grid(row=0, column=1, sticky=tk.W)

        def outputdir_clicked():
            self.outputpath = tkfd.askdirectory()
            outputEntry.insert(tk.END, self.outputpath)

        def output_cleardir_clicked():
            outputEntry.delete(0, tk.END)

        def getref_ellipse_clicked():
            input = Path(accuminputEntry.get())
            output = Path(outputEntry.get())
            numbeams = int(beamsEntry.get())
            minsize = int(minEntry.get())
            maxsize = int(maxEntry.get())
            binthresh = int(threshEntry.get())
            self.create_reference.main(input,output,numbeams,minsize,maxsize,binthresh)

        def accum_inputdir_clicked():
            self.accum_inputpath = tkfd.askdirectory()
            accuminputEntry.insert(tk.END, self.accum_inputpath)

        def accum_input_cleardir_clicked():
            accuminputEntry.delete(0, tk.END)

        def accum_outputdir_clicked():
            self.accum_outputpath = tkfd.askdirectory()
            accumoutputEntry.insert(tk.END, self.accum_outputpath)

        def accum_output_cleardir_clicked():
            accumoutputEntry.delete(0, tk.END)

        def accum_ellipse_clicked():
            ref = Path(outputEntry.get())
            input = Path(accuminputEntry.get())
            output = accumoutputEntry.get()
            numbeams = int(beamsEntry.get())
            self.accumulate_intensity.main(ref,input,output,numbeams)
            ArrangeValue(output).arrange_value()

        def fwhm_outputdir_clicked():
            self.fwhm_outputpath = tkfd.askdirectory()
            fwhmoutputEntry.insert(tk.END, self.fwhm_outputpath)

        def fwhm_output_cleardir_clicked():
            fwhmoutputEntry.delete(0, tk.END)

        def fwhm_ellipse_clicked():
            ref = Path(outputEntry.get())
            input = Path(accuminputEntry.get())
            output = fwhmoutputEntry.get()
            FWHM().fwhm(ref, input, output)

        self.accum_inputdir = tk.Button(configelipseFrame, text='Select', command=accum_inputdir_clicked)
        self.accum_inputdir.grid(row=1, column=2, sticky=tk.W)
        self.accum_input_cleardir = tk.Button(configelipseFrame, text='Clear', command=accum_input_cleardir_clicked)
        self.accum_input_cleardir.grid(row=1, column=3, sticky=tk.W)
        self.outputdir = tk.Button(configelipseFrame,text='Select', command=outputdir_clicked)
        self.outputdir.grid(row=2,column=2, sticky=tk.W)
        self.output_cleardir = tk.Button(configelipseFrame, text='Clear', command=output_cleardir_clicked)
        self.output_cleardir.grid(row=2, column=3, sticky=tk.W)

        self.getref_ellipse = tk.Button(ellipseparamFrame,text='Detect beam shapes', command=getref_ellipse_clicked)
        self.getref_ellipse.grid(row=2, column=2, sticky=tk.W,pady=5)

        self.accum_outputdir = tk.Button(accumellipseFrame,text='Select', command=accum_outputdir_clicked)
        self.accum_outputdir.grid(row=0,column=2, sticky=tk.W)
        self.accum_output_cleardir = tk.Button(accumellipseFrame, text='Clear', command=accum_output_cleardir_clicked)
        self.accum_output_cleardir.grid(row=0, column=3, sticky=tk.W)
        self.accum_ellipse = tk.Button(accumellipseFrame,text='Accumulate intensity of beams', command=accum_ellipse_clicked)
        self.accum_ellipse.grid(row=1,column=3, sticky=tk.W,pady=5)

        self.fwhm_outputdir = tk.Button(fwhmFrame, text='Select', command=fwhm_outputdir_clicked)
        self.fwhm_outputdir.grid(row=0, column=2, sticky=tk.W)
        self.fwhm_output_cleardir = tk.Button(fwhmFrame, text='Clear', command=fwhm_output_cleardir_clicked)
        self.fwhm_output_cleardir.grid(row=0, column=3, sticky=tk.W)
        self.fwhm_ellipse = tk.Button(fwhmFrame, text='Get short/long axis and Detect FWHM',
                                       command=fwhm_ellipse_clicked)
        self.fwhm_ellipse.grid(row=1, column=1, sticky=tk.W, pady=5)

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
        trainEntry = tk.Entry(dnnFrame,width=80)  # widthプロパティで大きさを変える
        #trainEntry.insert(tk.END,u'C:/Users/ryoya/PycharmProjects/terahertz-image-tools/sample/train')
        trainEntry.grid(row=1,column=1,sticky=tk.W)
        valEntry = tk.Entry(dnnFrame,width=80)  # widthプロパティで大きさを変える
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

        def trainfolderbutton_clear_clicked():
            trainEntry.delete(0, tk.END)

        def valfolderbutton_clicked():
            valpath = tkfd.askdirectory(title='検証(val)フォルダを選択してください')
            valEntry.insert(tk.END, valpath)

        def valfolderbutton_clear_clicked():
            valEntry.delete(0, tk.END)

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
                self.cvv = None
                self.cvv = ShowInfraredCamera()
                imtype = rdo_txt[rdo_var.get()]
                if imtype == 'image':
                    trigger_type = self.trigger_rdo_txt[self.trigger_rdo_var.get()]
                    gainEntry_value = int(self.gainEntry.get())
                    expEntry_value = int(self.expEntry.get())
                    dnn_classifier = DNNClasifier(imtype, trainEntry.get(), valEntry.get())
                    th = threading.Thread(target=dnn_classifier.test, args=(trigger_type,gainEntry_value,expEntry_value, self.cvv))
                    th.start()
                else:
                    messagebox.showerror('selecterror', '現在ビームの積算の値を用いた識別は実装されていません。imageを選択してください。')

            except RuntimeError:
                messagebox.showerror('connecterror','USBにカメラが接続されていません。')

        def dnn_test_color_clicked():
            try:
                self.cvv = None
                self.cvv = ShowInfraredCamera()
                imtype = rdo_txt[rdo_var.get()]
                if imtype == 'image':
                    trigger_type = self.trigger_rdo_txt[self.trigger_rdo_var.get()]
                    gainEntry_value = int(self.gainEntry.get())
                    expEntry_value = int(self.expEntry.get())
                    dnn_classifier = DNNClasifier(imtype, trainEntry.get(), valEntry.get())
                    th = threading.Thread(target=dnn_classifier.test_color, args=(trigger_type,gainEntry_value,expEntry_value, self.cvv))
                    th.start()
                else:
                    messagebox.showerror('selecterror', '現在ビームの積算の値を用いた識別は実装されていません。imageを選択してください。')

            except RuntimeError:
                messagebox.showerror('connecterror','USBにカメラが接続されていません。')

        self.trainfolderbutton = tk.Button(dnnFrame,text='Select', command=trainfolderbutton_clicked)
        self.trainfolderbutton.grid(row=1,column=2)
        self.trainfolderbutton_clear = tk.Button(dnnFrame, text='Clear', command=trainfolderbutton_clear_clicked)
        self.trainfolderbutton_clear.grid(row=1, column=3)
        self.valfolderbutton = tk.Button(dnnFrame,text='Select', command=valfolderbutton_clicked)
        self.valfolderbutton.grid(row=2,column=2)
        self.valfolderbutton_clear = tk.Button(dnnFrame, text='Clear', command=valfolderbutton_clear_clicked)
        self.valfolderbutton_clear.grid(row=2, column=3)
        self.trainbutton = tk.Button(dnnFrame,text='Train', command=dnn_train_clicked)
        self.trainbutton.grid(row=1,column=4)
        self.statusbutton = tk.Button(dnnFrame,text='Update status', command=status_clicked)
        self.statusbutton.grid(row=1,column=5)
        self.testbutton = tk.Button(dnnFrame,text='Realtime-Predict', command=dnn_test_clicked)
        self.testbutton.grid(row=2,column=4)
        self.testcolorbutton = tk.Button(dnnFrame, text='Realtime-Predict (カラー)', command=dnn_test_color_clicked)
        self.testcolorbutton.grid(row=2, column=5)


class Main:
    def __init__(self):
        self.gui=GUI()
        self.gui.root.mainloop()


if __name__=="__main__":
    Main()

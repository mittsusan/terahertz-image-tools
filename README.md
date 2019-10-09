# terahertz-image-tools

## セットアップ

### 動作確認済みの環境

- Windows 8.1
- Python `3.6.8`
- OpenCV `4.1.0`
- Spinnaker bindings for Python 3.6 (64bit) `1.23.0.27`

`pip list`の出力は以下の通り

```
$ python -m pip list
Package          Version
---------------- ---------
autopep8         1.4.4
backcall         0.1.0
colorama         0.4.1
cycler           0.10.0
decorator        4.4.0
entrypoints      0.3
flake8           3.7.7
ipython          7.5.0
ipython-genutils 0.2.0
jedi             0.14.0
kiwisolver       1.1.0
llvmlite         0.29.0
matplotlib       3.1.0
mccabe           0.6.1
numba            0.45.1
numpy            1.16.4
opencv-python    4.1.0.25
parso            0.5.0
pickleshare      0.7.5
pip              19.1.1
prompt-toolkit   2.0.9
pycodestyle      2.5.0
pyflakes         2.1.1
Pygments         2.4.2
pyparsing        2.4.0
python-dateutil  2.8.0
setuptools       40.6.2
six              1.12.0
spinnaker-python 1.23.0.27
traitlets        4.3.2
wcwidth          0.1.7
```

### 環境構築

Python 3.6.8を[公式ページ](https://www.python.org/downloads/)からダウンロードしてインストールする

`numpy`をインストールする

```
$ python -m pip install numpy
```

`opencv-python`をインストールする

```
$ python -m pip install opencv-python
```

Spinnaker SDKを[公式ページ](https://www.flir.com/products/spinnaker-sdk/)からダウンロードしてインストールする  
同梱されている`README.txt`に沿ってインストールを進める

以下が正しく実行できれば正しくインストールされている  
(バージョンは異なる可能性がある)

```
$ python -c "import numpy as np; print(np.__version__)"
1.16.4
$ python -c "import cv2; print(cv2.__version__)"
4.1.0
$ python -c "import PySpin"
```

## ファイルの説明

サンプルプログラム

- `accumulate_intensity.py`: 事前に作成した楕円マスクをもとに，楕円マスク内の画素輝度値を積算するサンプルプログラム
- `acquire_image.py`: カメラから画像を取得するサンプルプログラム
- `create_reference.py`: リファレンス画像から楕円マスクを作成するサンプルプログラム

モジュール

- `module/beem_accumulator.py`: 事前に作成した楕円マスクをもとに，楕円マスク内の画素輝度値を積算するモジュール
- `module/camera_manager.py`: カメラへのアクセスを行うモジュール
- `module/ellipse_detector.py`: 楕円検出を行うモジュール

テスト用ファイル

- `sample/None`: サンプルの挿入無しで撮影したビーム画像 x 10
- `sample/Si_0_05mm`: 0.05mmのSi基板を挿入して撮影したビーム画像 x 10
- `sample/Si_0_10mm`: 0.10mmのSi基板を挿入して撮影したビーム画像 x 10
- `sample/Si_0_20mm`: 0.20mmのSi基板を挿入して撮影したビーム画像 x 10

## 使い方

### `accumulate_intensity.py`

オプションは以下の通り  
デフォルト値はプログラムを参照してください

- トリガの種類 (`hardware`/`software`)
- `--exp`: 露出時間[us]
- `--gain`: ゲイン[db]
- `--save-dir`: 画像を保存するディレクトリ
- `--num-imgs`: 保存する画像枚数

以下のように実行する

```
$ python accumulate_intensity.py hardware --exp 20000 --gain 10 --save-dir /path/to/save/dir --num-imgs 100
```

サンプルプログラムでは自動露出をOFF，撮影モードをCONTINUOUSにしているが，プログラムを変更することでこれらを切り替えることも可能である

### `create_reference.py`

オプションは以下の通り  
デフォルト値はプログラムを参照してください

- 入力画像を格納したディレクトリ
- `--output`: 楕円パラメータと楕円マスクを保存するディレクトリ
- `--num-beams`: ビームの本数
- `--min-size`: 楕円の短軸長の最小閾値
- `--max-size`: 楕円の短軸長の最大閾値
- `--bin-thresh`: 二値化の閾値 (0の場合，Otsu's methodが使われる)

以下のように実行する

```
$ python create_reference.py sample\None --output ref --num-beams 3
detecting ellipses from sample\None\000000.png ...
detecting ellipses from sample\None\000001.png ...
detecting ellipses from sample\None\000002.png ...
detecting ellipses from sample\None\000003.png ...
detecting ellipses from sample\None\000004.png ...
detecting ellipses from sample\None\000005.png ...
detecting ellipses from sample\None\000006.png ...
detecting ellipses from sample\None\000007.png ...
detecting ellipses from sample\None\000008.png ...
detecting ellipses from sample\None\000009.png ...
averaging ellipse parameters ...

[beam 0]
center x   : 335.4783935546875
center y   : 1080.272900390625
minor axis : 165.34539794921875
major axis : 237.35079650878907
angle      : 3.944380521774292

[beam 1]
center x   : 976.9233215332031
center y   : 1086.1546875
minor axis : 142.7715270996094
major axis : 244.6910629272461
angle      : 179.54207611083984

[beam 2]
center x   : 1409.5835693359375
center y   : 1099.5423706054687
minor axis : 111.31228866577149
major axis : 185.2999526977539
angle      : 178.44988250732422

integrating ellipse masks ...
saving ellipse information to ref ...
```

統合された楕円マスクが表示され，`ref`に楕円パラメータと楕円マスクが保存される

### `accumulate_intensity.py`

オプションは以下の通り  
デフォルト値はプログラムを参照してください

- 楕円パラメータと楕円マスクを格納したディレクトリ
- 入力画像を格納したディレクトリ
- `--num-beams`: ビームの本数

以下のように実行する

```
$ python accumulate_intensity.py ref sample\Si_0_05mm

image: C:\Users\sumikura\Programs\terahertz-image-tools\sample\Si_0_05mm\000000.png
------------------------------
beam name    average
------------------------------
00           54.44823292788047
01           113.23023358632378
02           51.359641035097425
------------------------------

image: C:\Users\sumikura\Programs\terahertz-image-tools\sample\Si_0_05mm\000001.png
------------------------------
beam name    average
------------------------------
00           54.90297864189254
01           116.70031685211111
02           51.67668572131047
------------------------------

image: C:\Users\sumikura\Programs\terahertz-image-tools\sample\Si_0_05mm\000002.png
------------------------------
beam name    average
------------------------------
00           54.02716853430387
01           112.60691916586839
02           51.8862868031225
------------------------------

image: C:\Users\sumikura\Programs\terahertz-image-tools\sample\Si_0_05mm\000003.png
------------------------------
beam name    average
------------------------------
00           53.25007183219998
01           109.11616682632084
02           51.28047206343352
------------------------------

image: C:\Users\sumikura\Programs\terahertz-image-tools\sample\Si_0_05mm\000004.png
------------------------------
beam name    average
------------------------------
00           51.25559493024295
01           108.8252155331221
02           52.03362222632
------------------------------

image: C:\Users\sumikura\Programs\terahertz-image-tools\sample\Si_0_05mm\000005.png
------------------------------
beam name    average
------------------------------
00           53.97069246240782
01           112.79474614987842
02           51.778843198721496
------------------------------

image: C:\Users\sumikura\Programs\terahertz-image-tools\sample\Si_0_05mm\000006.png
------------------------------
beam name    average
------------------------------
00           52.63116559716502
01           109.97608871859111
02           50.948306595365416
------------------------------

image: C:\Users\sumikura\Programs\terahertz-image-tools\sample\Si_0_05mm\000007.png
------------------------------
beam name    average
------------------------------
00           52.279155891836666
01           110.04767518974283
02           53.07806257299158
------------------------------

image: C:\Users\sumikura\Programs\terahertz-image-tools\sample\Si_0_05mm\000008.png
------------------------------
beam name    average
------------------------------
00           52.26897168215049
01           115.32554712254071
02           51.74356137439302
------------------------------

image: C:\Users\sumikura\Programs\terahertz-image-tools\sample\Si_0_05mm\000009.png
------------------------------
beam name    average
------------------------------
00           53.51731954155094
01           115.64917839510721
02           52.308869629356444
------------------------------
```

各楕円マスク内領域の画素輝度値の平均値が表示される

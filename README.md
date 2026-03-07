# High-Precision AI Background Remover (bg_remover2)

商用レベルの高精度なAI背景透過ツールです。「フキダシ内の文字」や「意図的な白フチ（余白）」などを消さずに、被写体と背景を完璧に分離します。

## 特徴
- **最高精度のAIモデルを使用**: 背景透過に特化した強力なAIモデル `briaai/RMBG-1.4` を採用し、Canva等の有料ツールと同等レベルのクオリティを実現しています。
- **白フチ・文字の保持**: よくある「服の白い部分や文字まで削れてしまう」問題を、独自の二値化・しきい値調整ロジックで解決しています。
- **どのような画像サイズでも対応**: 長方形、正方形問わず、アスペクト比を維持したまま処理が可能です。
- **UIとロジックの分離**: 直観的なGradioベースのWeb UI(`app.py`)と、外部ツールから呼び出しやすいコアロジック(`core.py`)が分離されています。

## ファイル構成
- `app.py`: ドラッグ＆ドロップで画像を透過できるGradio製のWeb UIアプリです。
- `core.py`: 背景透過の推論を行うコアロジックです。他のシステム（CLIや外部アプリ）からの組み込み利用が可能です。
- `briarmbg.py` / `utilities.py` / `MyConfig.py` / `MyPipe.py`: Hugging Faceからのモデル推論に必要なコンポーネント群です。

## インストール方法

1. リポジトリをクローンします。
```bash
git clone https://github.com/oresama5656/bg_remover2.git
cd bg_remover2
```

2. 必要なライブラリをインストールします。
```bash
pip install -r requirements.txt
```
*(※必要に応じて `torch`, `torchvision`, `scikit-image`, `huggingface_hub` 等が含まれていることを確認してください)*

## 使い方

### Web UI (Gradio) で使う
以下のコマンドでローカルサーバーを起動し、ブラウザでアクセスします。
```bash
python app.py
```
起動後、コンソールに表示されるURL（例: `http://127.0.0.1:7860`）にアクセスし、画像をドラッグ＆ドロップしてください。

### Pythonスクリプトから呼び出す
他のプロジェクトから `core.py` を呼び出して利用することも簡単です。
```python
from PIL import Image
from core import remove_background

# 画像を読み込み
img = Image.open('input.png')

# 背景切り抜きを実行
output_img = remove_background(img)

# 保存
output_img.save('output.png', format="PNG")
```

## 注意事項
- 初回起動時のみ、Hugging Faceから `RMBG-1.4` のモデル本体 (`model.pth`) が自動的にダウンロードされます（約170MB程度）。通信環境の良い場所で実行してください。

import os
import torch
import torch.nn.functional as F
from PIL import Image
from huggingface_hub import hf_hub_download
from torchvision.transforms.functional import normalize

# huggingface_hubから取得したスクリプトをインポート
from briarmbg import BriaRMBG
from utilities import preprocess_image, postprocess_image

def init_session():
    """
    HuggingFaceからRMBG-1.4モデルの重みをダウンロードし、初期化します。
    """
    net = BriaRMBG()
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    
    # model.pthをキャッシュディレクトリにダウンロードしてパスを取得
    try:
        model_path = hf_hub_download("briaai/RMBG-1.4", "model.pth")
    except Exception as e:
        print(f"Error downloading model: {e}")
        return None

    if torch.cuda.is_available():
        net.load_state_dict(torch.load(model_path))
        net = net.cuda()
    else:
        net.load_state_dict(torch.load(model_path, map_location="cpu"))
        
    net.eval()
    return net, device

# グローバルセッションを初期化 (app実行時に使い回すため)
NET, DEVICE = init_session()

def remove_background(input_image: Image.Image, threshold: int = 50) -> Image.Image:
    """
    PillowのImageオブジェクトを受け取り、背景透過後のImageオブジェクトを返します。
    """
    if NET is None:
        raise RuntimeError("モデルの初期化に失敗しています。")

    # RGBに変換してサイズを取得
    if input_image.mode != "RGB":
        input_image = input_image.convert("RGB")
    
    # 既存のutilities.pyの前処理関数を使用
    # モデルの推奨入力サイズは [1024, 1024]
    model_input_size = [1024, 1024]
    orig_im_size = input_image.size
    
    # テンソルへの変換と前処理
    import numpy as np
    im_np = np.array(input_image)
    im_tensor = preprocess_image(im_np, model_input_size).to(DEVICE)

    # 推論の実行
    with torch.no_grad():
        result = NET(im_tensor)
        
    # リザルトテンソルからマスクを取得し、後処理を実行 (元のサイズに戻す)
    result_tensor = result[0][0]
    
    # PyTorchのF.interpolateは size=(Height, Width) を想定しているため、Pillowの(W, H)を反転して渡す
    orig_im_size_hw = (input_image.height, input_image.width)
    result_image = postprocess_image(result_tensor, orig_im_size_hw)
    
    # 【調整箇所】
    # result_imageのピクセルは0〜255の範囲。
    # しきい値を下げて、少しでも被写体らしき部分（薄いグレー等）は完全に残す(255にする)処理を追加する。
    # 閾値を引数で受け取るように変更（0(残る)〜255(削れる)）
    if threshold is not None and 0 <= threshold <= 255:
        im_mask_np = np.where(result_image > threshold, 255, 0).astype(np.uint8)
        pil_mask = Image.fromarray(im_mask_np).convert("L")
    else:
        pil_mask = Image.fromarray(result_image).convert("L")
    
    # バグ修正: input_image と pil_mask のサイズが（縦横の1ピクセル単位で）異なる場合に備え、
    # 確実に input_image の元のサイズにリサイズしてからアルファチャンネルとして適用する
    if pil_mask.size != input_image.size:
        pil_mask = pil_mask.resize(input_image.size, Image.Resampling.LANCZOS)
    
    # マスクを適用するためにRGBA画像を作成
    image_rgba = input_image.convert("RGBA")
    image_rgba.putalpha(pil_mask)

    return image_rgba

def process_image_file(input_path: str, output_path: str):
    """
    (将来のバッチ処理やCLI用) ファイルパスから画像を読み込み、透過して保存します。
    """
    image = Image.open(input_path)
    output_image = remove_background(image)
    output_image.save(output_path, format="PNG")

if __name__ == "__main__":
    # 動作確認用スクリプト
    import sys
    if len(sys.argv) > 2:
        in_path = sys.argv[1]
        out_path = sys.argv[2]
        print(f"Processing {in_path} -> {out_path} ...")
        process_image_file(in_path, out_path)
        print("Done.")
    else:
        print("Usage: python core.py <input_image_path> <output_image_path>")

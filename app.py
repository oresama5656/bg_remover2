import gradio as gr
from PIL import Image
from core import remove_background, init_session

def process_interface(input_image, threshold, binarize):
    """
    Gradioのインターフェースから呼び出される関数。
    入力画像を受け取り、core.pyの関数で処理して返す。
    """
    if input_image is None:
        return None
    
    # 二値化するかどうかの分岐
    thresh_val = int(threshold) if binarize else -1
    
    # PIL形式のImageオブジェクトで受け取り、PIL形式で返す
    output_image = remove_background(input_image, threshold=thresh_val)
    return output_image

# Gradio インターフェースの構築
with gr.Blocks(title="AI Background Remover") as demo:
    gr.Markdown("# 高精度AI背景透過ツール")
    gr.Markdown("ドラッグ＆ドロップで画像をアップロードすると、AIが高精度で背景を透过します。\n黒い背景等が残ってしまう場合は「エッジをくっきりさせる(二値化)」のチェックを外し、滑らかな透過を試してください。")
    
    with gr.Row():
        with gr.Column():
            input_image = gr.Image(type="pil", label="元画像 (ドラッグ＆ドロップで追加)")
            binarize_chk = gr.Checkbox(label="エッジをくっきりさせる（二値化）", value=False, info="白フチを強制的に残す場合はチェックを入れてください。黒背景などでゴミが残る場合はチェックを外してください。")
            threshold_slider = gr.Slider(minimum=0, maximum=255, step=1, value=50, label="白フチ強調/背景残り調整 (閾値)", info="二値化ON時のみ有効。数値を上げるとフチが削れやすくなり、下げると少しのフチでも残します。")
            process_btn = gr.Button("透過処理を実行", variant="primary")
        
        with gr.Column():
            # 処理結果はPNGでダウンロードできるようにする
            output_image = gr.Image(type="pil", label="透過後画像", interactive=False)
            
    # ボタンクリック時の動作を定義
    process_btn.click(
        fn=process_interface,
        inputs=[input_image, threshold_slider, binarize_chk],
        outputs=[output_image],
        api_name="remove_bg"
    )

if __name__ == "__main__":
    # 自動でブラウザを開かず、ローカルで起動する
    # hostを0.0.0.0にするとネットワーク内からアクセス可能になる
    demo.launch(server_name="127.0.0.1", server_port=7860, inbrowser=False, share=False)

import os
from hide.video_steganography import embed_message, extract_message
from hide.utils import get_video_path, get_output_video_path, get_extracted_video_path

def test_video_steg():
    original_video = get_video_path("input.mp4")
    output_video = get_output_video_path("output_with_hidden_data.avi")
    extracted_file = get_extracted_video_path("extracted_secret.bin")
    secret = b"hello, this is a secret message!"

    # 嵌入
    embed_message(original_video, output_video, secret)
    # 提取
    extracted = extract_message(output_video)
    with open(extracted_file, "wb") as f:
        f.write(extracted)
    print("视频隐写测试：", extracted == secret)

if __name__ == "__main__":
    test_video_steg()
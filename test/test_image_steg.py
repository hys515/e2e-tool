import os
from hide.image_steganography import embed_message, extract_message
from hide.utils import get_image_path, get_output_image_path, get_extracted_image_path

def test_image_steg():
    original_image = get_image_path("cover.png")
    output_image = get_output_image_path("cover_embedded.png")
    extracted_file = get_extracted_image_path("extracted_secret.bin")
    secret = b"hello, this is a secret message!"

    # 嵌入
    embed_message(original_image, output_image, secret, n_bits=1)
    # 提取
    extracted = extract_message(output_image, n_bits=1)
    with open(extracted_file, "wb") as f:
        f.write(extracted)
    print("图片隐写测试：", extracted == secret)

if __name__ == "__main__":
    test_image_steg()
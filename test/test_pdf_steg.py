import os
from hide.pdf_steganography import embed_message, extract_message
from hide.utils import get_pdf_path, get_output_pdf_path, get_extracted_pdf_path

def test_pdf_steg():
    original_pdf = get_pdf_path("cover.pdf")
    output_pdf = get_output_pdf_path("cover_embedded.pdf")
    extracted_file = get_extracted_pdf_path("extracted_secret.bin")
    secret = b"hello, this is a secret message!"

    # 嵌入
    embed_message(original_pdf, output_pdf, secret)
    # 提取
    extracted = extract_message(output_pdf)
    with open(extracted_file, "wb") as f:
        f.write(extracted)
    print("PDF隐写测试：", extracted == secret)

if __name__ == "__main__":
    test_pdf_steg()

# hide/steg.py

def embed_message(carrier_type, input_path, output_path, message: bytes):
    """
    carrier_type: 'image' | 'pdf' | 'video'
    input_path: 原始载体文件路径
    output_path: 隐写输出文件路径
    message: 要嵌入的字节串
    """
    if carrier_type == 'image':
        from .image_steganography import embed_message as image_embed
        return image_embed(input_path, output_path, message)
    elif carrier_type == 'pdf':
        from .pdf_steganography import embed_message as pdf_embed
        return pdf_embed(input_path, output_path, message)
    elif carrier_type == 'video':
        from .video_steganography import embed_message as video_embed
        return video_embed(input_path, output_path, message)
    else:
        raise ValueError(f"不支持的载体类型: {carrier_type}")

def extract_message(carrier_type, stego_path):
    """
    carrier_type: 'image' | 'pdf' | 'video'
    stego_path: 隐写文件路径
    return: 提取出的字节串
    """
    if carrier_type == 'image':
        from .image_steganography import extract_message as image_extract
        return image_extract(stego_path)
    elif carrier_type == 'pdf':
        from .pdf_steganography import extract_message as pdf_extract
        return pdf_extract(stego_path)
    elif carrier_type == 'video':
        from .video_steganography import extract_message as video_extract
        return video_extract(stego_path)
    else:
        raise ValueError(f"不支持的载体类型: {carrier_type}")
import ctypes
import os

# 修改为你的实际 GmSSL 动态库路径
GMSL_LIB_PATH = '/usr/local/lib/libgmssl.dylib'  # macOS
# GMSL_LIB_PATH = '/usr/local/lib/libgmssl.so'  # Linux

if not os.path.exists(GMSL_LIB_PATH):
    raise FileNotFoundError(f"GmSSL动态库未找到: {GMSL_LIB_PATH}")

lib = ctypes.cdll.LoadLibrary(GMSL_LIB_PATH)

zuc_encrypt = lib.zuc_encrypt
zuc_encrypt.argtypes = [
    ctypes.c_char_p, ctypes.c_char_p,
    ctypes.c_char_p, ctypes.c_size_t,
    ctypes.c_char_p
]
zuc_encrypt.restype = ctypes.c_int

def zuc_encrypt_py(key: bytes, iv: bytes, data: bytes) -> bytes:
    if not (isinstance(key, bytes) and isinstance(iv, bytes) and isinstance(data, bytes)):
        raise TypeError("key, iv, data 必须为 bytes 类型")
    if len(key) != 16 or len(iv) != 16:
        raise ValueError("key 和 iv 必须为16字节")
    if len(data) == 0:
        raise ValueError("data 不能为空")
    outbuf = ctypes.create_string_buffer(len(data))
    ret = zuc_encrypt(key, iv, data, len(data), outbuf)
    if ret != 1:
        raise RuntimeError("zuc_encrypt failed")
    return outbuf.raw

# 解密时也用 zuc_encrypt_py
zuc_decrypt_py = zuc_encrypt_py

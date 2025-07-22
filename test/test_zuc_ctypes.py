from crypto.zuc_ctypes import zuc_encrypt_py, zuc_decrypt_py
import os

key = os.urandom(16)
iv = os.urandom(16)
plaintext = b'hello world'
print(f"key: {key.hex()} iv: {iv.hex()} plaintext: {plaintext}")
ciphertext = zuc_encrypt_py(key, iv, plaintext)
print(f"ciphertext: {ciphertext.hex()}")
decrypted = zuc_decrypt_py(key, iv, ciphertext)
print(f"decrypted: {decrypted}")
assert decrypted == plaintext
print("ZUC加解密测试通过")
import os
import time
import subprocess
import hashlib

os.makedirs("perf_test", exist_ok=True)

lengths = [2**n for n in range(4, 22)]  # 从 16B 到 4MB

print(f"{'Size (bytes)':>12} | {'Enc Time (ms)':>14} | {'Dec Time (ms)':>14} | {'OK?'}")
print("-" * 55)

for size in lengths:
    infile = f"test/data/input_{size}.txt"
    cipherfile = f"test/data/cipher_{size}.zuc"
    recovered = f"test/data/recovered_{size}.txt"

    # 生成指定长度的随机明文
    with open(infile, "wb") as f:
        f.write(os.urandom(size))

    # 加密
    t1 = time.time()
    subprocess.run(["./e2e-tool", "encrypt", "-in", infile, "-out", cipherfile], check=True, stdout=subprocess.DEVNULL)
    t2 = time.time()

    # 解密
    t3 = time.time()
    subprocess.run(["./e2e-tool", "decrypt", "-in", cipherfile, "-out", recovered, "-key", "zuc.key"], check=True, stdout=subprocess.DEVNULL)
    t4 = time.time()

    # 校验明文一致性
    with open(infile, "rb") as f1, open(recovered, "rb") as f2:
        ok = hashlib.sha256(f1.read()).digest() == hashlib.sha256(f2.read()).digest()

    print(f"{size:12} | {(t2 - t1)*1000:14.2f} | {(t4 - t3)*1000:14.2f} | {'✅' if ok else '❌'}")

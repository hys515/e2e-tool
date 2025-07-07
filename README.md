# 🔐 E2E-Tool：基于 GmSSL 的 ZUC 静态加密工具

**E2E-Tool** 是一个基于 GmSSL 实现的命令行加密工具，采用国密 ZUC 算法进行流加密，**已静态链接 GmSSL 加密库**，可在 macOS/Linux 系统上直接运行，无需预先安装 GmSSL。

本工具适用于构建端到端加密（E2EE）系统的“加解密模块”，输出为纯粹的二进制密文，便于与信息隐藏模块对接。

---

## 🔧 使用的 GmSSL 接口

本工具在底层调用了 GmSSL 提供的以下 C 接口：

- `zuc_encrypt(...)`：执行 ZUC 加密（流密码）
- `rand_bytes(...)`：用于生成 128-bit ZUC 加密密钥（使用系统安全随机数源）

---

## 🚀 工具用途与功能

该命令行工具提供两大功能：

| 功能 | 描述 |
|------|------|
| 🔐 加密 | 输入明文，输出密文（`.zuc` 二进制文件），并生成密钥文件 |
| 🔓 解密 | 使用密钥文件还原密文，恢复原始明文 |

---

## 🛠️ 使用方法

### 🔐 加密

```bash
./e2e-tool encrypt -in <明文路径> -out <密文输出路径>
````

示例：

```bash
./e2e-tool encrypt -in test/message.txt -out test/cipher.zuc
```

执行后生成两个文件：

* `cipher.zuc`：加密后的密文（二进制）
* `zuc.key`：对应的 128-bit 加密密钥

---

### 🔓 解密

```bash
./e2e-tool decrypt -in <密文路径> -out <明文输出路径> -key zuc.key
```

示例：

```bash
./e2e-tool decrypt -in test/cipher.zuc -out test/recovered.txt -key zuc.key
```

如果密钥正确，输出文件将与原始明文一致。

---

## 🧪 性能测试（可选）

项目包含自动化脚本 `test_perf.py`，用于批量测试不同明文长度下的加解密耗时与正确性。

运行：

```bash
python3 test_perf.py
```

输出示例：

```
Size (bytes) |  Enc Time (ms) |  Dec Time (ms) | OK?
-------------------------------------------------------
       128   |         0.25   |         0.21   | ✅
     65536   |         3.91   |         3.82   | ✅
```

---

## 📦 项目结构

```text
e2e_tool/
├── e2e-tool           # 可执行命令行工具（静态链接 GmSSL）
├── test_perf.py       # 性能测试脚本（可选使用）
├── README.md
```

---

## 🔭 下一阶段开发模块（规划中）

* 🧾 **用户身份管理**（证书生成 / 请求 / 签名，基于 GmSSL 的 `certgen`, `reqgen` 等）
* 🔐 **密钥协商机制**（例如 SM2 密钥封装，或 DH/SM2 混合方案）
* 🖼️ **信息隐藏模块对接**（对密文进行图像/媒体文件嵌入）
* 🌐 **消息传输协议封装**（如 TLS/SM4 over UDP/TCP）

---

## 📜 License

本项目为研究用途构建，使用 GmSSL 项目作为底层加密引擎。请遵循 GmSSL 的使用与分发许可。


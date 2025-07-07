#ifndef SM2_ECDH_H
#define SM2_ECDH_H

#ifdef __cplusplus
extern "C" {
#endif

// 生成SM2密钥对，并保存为私钥和公钥文件
int sm2_generate_keypair(const char *privkey_path, const char *pubkey_path);

// 使用ECDH协商共享密钥，输出为64字节（512位）session key
int sm2_derive_session_key(const char *privkey_path, const char *peer_pubkey_path, const char *out_keyfile);

#ifdef __cplusplus
}
#endif

#endif // SM2_ECDH_H

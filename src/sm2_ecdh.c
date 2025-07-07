#include <stdio.h>
#include <stdint.h>
#include <string.h>
#include <gmssl/sm2.h>
#include <gmssl/pem.h>
#include <gmssl/error.h>
#include "sm2_ecdh.h"

int sm2_generate_keypair(const char *privkey_path, const char *pubkey_path) {
    SM2_KEY key;

    if (!sm2_key_generate(&key)) {
        fprintf(stderr, "[-] Failed to generate SM2 key\n");
        return -1;
    }

    // 写入私钥
    FILE *fp = fopen(privkey_path, "w");
    if (!fp) {
        perror("fopen priv");
        return -1;
    }
    if (sm2_private_key_to_pem(&key, fp) != 1) {
        fprintf(stderr, "[-] Failed to write private key\n");
        fclose(fp);
        return -1;
    }
    fclose(fp);

    // 写入公钥（用 info 接口）
    fp = fopen(pubkey_path, "w");
    if (!fp) {
        perror("fopen pub");
        return -1;
    }
    if (sm2_public_key_info_to_pem(&key, fp) != 1) {
        fprintf(stderr, "[-] Failed to write public key\n");
        fclose(fp);
        return -1;
    }
    fclose(fp);

    return 0;
}

int sm2_derive_session_key(const char *privkey_path, const char *peer_pubkey_path, const char *out_keyfile) {
    SM2_KEY local_key;
    SM2_KEY peer_key;
    uint8_t shared_key[64];
    uint8_t peer_public_octets[65]; // 65字节的未压缩格式公钥

    // 读取私钥
    FILE *fp = fopen(privkey_path, "r");
    if (!fp) {
        perror("fopen priv");
        return -1;
    }
    if (sm2_private_key_from_pem(&local_key, fp) != 1) {
        fprintf(stderr, "[-] Failed to read private key\n");
        fclose(fp);
        return -1;
    }
    fclose(fp);

    // 读取对方公钥
    fp = fopen(peer_pubkey_path, "r");
    if (!fp) {
        perror("fopen pub");
        return -1;
    }
    if (sm2_public_key_info_from_pem(&peer_key, fp) != 1) {
        fprintf(stderr, "[-] Failed to read peer public key\n");
        fclose(fp);
        return -1;
    }
    fclose(fp);

    // 将 SM2_Z256_POINT 转换为字节数组格式
    if (sm2_z256_point_to_uncompressed_octets(&peer_key.public_key, peer_public_octets) != 1) {
        fprintf(stderr, "[-] Failed to convert public key to octets\n");
        return -1;
    }

    // ECDH
    if (sm2_ecdh(&local_key,
                 peer_public_octets, // 使用转换后的字节数组
                 sizeof(peer_public_octets),
                 shared_key) != 1) {
        fprintf(stderr, "[-] SM2 ECDH key agreement failed\n");
        return -1;
    }

    // 写入共享密钥
    fp = fopen(out_keyfile, "wb");
    if (!fp) {
        perror("fopen out_key");
        return -1;
    }
    if (fwrite(shared_key, 1, sizeof(shared_key), fp) != sizeof(shared_key)) {
        fprintf(stderr, "[-] Failed to write shared key\n");
        fclose(fp);
        return -1;
    }

    fclose(fp);
    return 0;
}

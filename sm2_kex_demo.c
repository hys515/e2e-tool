#include <stdio.h>
#include <string.h>
#include <stdint.h>
#include <gmssl/sm2.h>
#include <gmssl/rand.h>

#define ID_CLIENT "ClientA"
#define ID_SERVER "ServerB"

int sm2_key_exchange(
    int is_initiator,
    size_t keylen,
    const SM2_KEY *local_static,
    const SM2_KEY *local_eph,
    const uint8_t *id_local, size_t id_local_len,
    const SM2_KEY *peer_static,
    const SM2_KEY *peer_eph,
    const uint8_t *id_peer, size_t id_peer_len,
    uint8_t *out_key, size_t *out_keylen);

int main(void) {
    int ret = -1;

    // 双方静态密钥对
    SM2_KEY client_static, server_static;

    // 双方临时密钥对
    SM2_KEY client_eph, server_eph;

    // 会话密钥输出缓冲
    uint8_t key_client[32] = {0};
    uint8_t key_server[32] = {0};
    size_t keylen_client = sizeof(key_client);
    size_t keylen_server = sizeof(key_server);

    // 初始化密钥对
    sm2_key_generate(&client_static);
    sm2_key_generate(&client_eph);

    sm2_key_generate(&server_static);
    sm2_key_generate(&server_eph);

    printf("[*] 密钥对已生成，开始协商...\n");

    // 客户端计算会话密钥（is_initiator = 1）
    if (!sm2_key_exchange(
            1,
            32,
            &client_static, &client_eph,
            (const uint8_t *)ID_CLIENT, strlen(ID_CLIENT),
            &server_static, &server_eph,
            (const uint8_t *)ID_SERVER, strlen(ID_SERVER),
            key_client, &keylen_client)) {
        fprintf(stderr, "[-] 客户端密钥协商失败\n");
        goto end;
    }

    // 服务端计算会话密钥（is_initiator = 0）
    if (!sm2_key_exchange(
            0,
            32,
            &server_static, &server_eph,
            (const uint8_t *)ID_SERVER, strlen(ID_SERVER),
            &client_static, &client_eph,
            (const uint8_t *)ID_CLIENT, strlen(ID_CLIENT),
            key_server, &keylen_server)) {
        fprintf(stderr, "[-] 服务端密钥协商失败\n");
        goto end;
    }

    printf("[+] 客户端密钥：");
    for (size_t i = 0; i < keylen_client; i++) {
        printf("%02X", key_client[i]);
    }
    printf("\n");

    printf("[+] 服务端密钥：");
    for (size_t i = 0; i < keylen_server; i++) {
        printf("%02X", key_server[i]);
    }
    printf("\n");

    // 验证一致性
    if (keylen_client == keylen_server &&
        memcmp(key_client, key_server, keylen_client) == 0) {
        printf("✅ 协商成功，双方会话密钥一致！\n");
        ret = 0;
    } else {
        fprintf(stderr, "❌ 密钥不一致，协商失败\n");
    }

end:
    return ret;
}

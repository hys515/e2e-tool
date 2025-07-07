#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <time.h>
#include <gmssl/sm2.h>
#include <gmssl/zuc.h>
#include <gmssl/rand.h>
#include "sm2_ecdh.h"

#define COLOR_GREEN  "\033[1;32m"
#define COLOR_RED    "\033[1;31m"
#define COLOR_YELLOW "\033[1;33m"
#define COLOR_BLUE   "\033[1;34m"
#define COLOR_RESET  "\033[0m"

#define TEST_DATA_SIZE 1024
#define ZUC_KEY_SIZE 16

// 测试结果统计
typedef struct {
    int total_tests;
    int passed_tests;
    int failed_tests;
} test_stats_t;

test_stats_t stats = {0, 0, 0};

// 测试辅助函数
void print_test_header(const char *test_name) {
    printf("\n%s=== %s ===%s\n", COLOR_BLUE, test_name, COLOR_RESET);
}

void print_test_result(const char *test_name, int passed) {
    if (passed) {
        printf("%s[✓] %s PASSED%s\n", COLOR_GREEN, test_name, COLOR_RESET);
        stats.passed_tests++;
    } else {
        printf("%s[✗] %s FAILED%s\n", COLOR_RED, test_name, COLOR_RESET);
        stats.failed_tests++;
    }
    stats.total_tests++;
}

void print_final_stats() {
    printf("\n%s=== 测试统计 ===%s\n", COLOR_BLUE, COLOR_RESET);
    printf("总测试数: %d\n", stats.total_tests);
    printf("通过: %s%d%s\n", COLOR_GREEN, stats.passed_tests, COLOR_RESET);
    printf("失败: %s%d%s\n", COLOR_RED, stats.failed_tests, COLOR_RESET);
    printf("成功率: %.1f%%\n", (float)stats.passed_tests / stats.total_tests * 100);
}

// 生成随机测试数据
void generate_test_data(unsigned char *data, size_t size) {
    for (size_t i = 0; i < size; i++) {
        data[i] = rand() % 256;
    }
}

// 比较两个数据块
int compare_data(const unsigned char *data1, const unsigned char *data2, size_t size) {
    return memcmp(data1, data2, size) == 0;
}

// 测试1: SM2 密钥生成
int test_sm2_key_generation() {
    print_test_header("SM2 密钥生成测试");
    
    const char *priv_file = "test_priv.pem";
    const char *pub_file = "test_pub.pem";
    
    // 清理旧文件
    unlink(priv_file);
    unlink(pub_file);
    
    // 生成密钥对
    int result = sm2_generate_keypair(priv_file, pub_file);
    if (result != 0) {
        print_test_result("SM2 密钥生成", 0);
        return 0;
    }
    
    // 检查文件是否存在
    FILE *fp = fopen(priv_file, "r");
    if (!fp) {
        print_test_result("私钥文件创建", 0);
        return 0;
    }
    fclose(fp);
    
    fp = fopen(pub_file, "r");
    if (!fp) {
        print_test_result("公钥文件创建", 0);
        return 0;
    }
    fclose(fp);
    
    print_test_result("SM2 密钥生成", 1);
    return 1;
}

// 测试2: SM2 ECDH 密钥协商
int test_sm2_ecdh() {
    print_test_header("SM2 ECDH 密钥协商测试");
    
    const char *alice_priv = "alice_priv.pem";
    const char *alice_pub = "alice_pub.pem";
    const char *bob_priv = "bob_priv.pem";
    const char *bob_pub = "bob_pub.pem";
    const char *alice_session = "alice_session.key";
    const char *bob_session = "bob_session.key";
    
    // 清理旧文件
    unlink(alice_priv); unlink(alice_pub);
    unlink(bob_priv); unlink(bob_pub);
    unlink(alice_session); unlink(bob_session);
    
    // 生成 Alice 和 Bob 的密钥对
    if (sm2_generate_keypair(alice_priv, alice_pub) != 0) {
        print_test_result("Alice 密钥生成", 0);
        return 0;
    }
    
    if (sm2_generate_keypair(bob_priv, bob_pub) != 0) {
        print_test_result("Bob 密钥生成", 0);
        return 0;
    }
    
    // Alice 与 Bob 的公钥协商
    if (sm2_derive_session_key(alice_priv, bob_pub, alice_session) != 0) {
        print_test_result("Alice 密钥协商", 0);
        return 0;
    }
    
    // Bob 与 Alice 的公钥协商
    if (sm2_derive_session_key(bob_priv, alice_pub, bob_session) != 0) {
        print_test_result("Bob 密钥协商", 0);
        return 0;
    }
    
    // 读取并比较会话密钥
    FILE *fp1 = fopen(alice_session, "rb");
    FILE *fp2 = fopen(bob_session, "rb");
    if (!fp1 || !fp2) {
        print_test_result("会话密钥文件读取", 0);
        return 0;
    }
    
    unsigned char alice_key[64], bob_key[64];
    size_t read1 = fread(alice_key, 1, 64, fp1);
    size_t read2 = fread(bob_key, 1, 64, fp2);
    fclose(fp1);
    fclose(fp2);
    
    if (read1 != 64 || read2 != 64) {
        print_test_result("会话密钥长度", 0);
        return 0;
    }
    
    // 验证 ECDH 正确性：两个密钥应该相同
    int keys_match = compare_data(alice_key, bob_key, 64);
    print_test_result("ECDH 密钥协商正确性", keys_match);
    
    return keys_match;
}

// 测试3: ZUC 加密解密
int test_zuc_encryption() {
    print_test_header("ZUC 加密解密测试");
    
    // 生成测试数据
    unsigned char test_data[TEST_DATA_SIZE];
    generate_test_data(test_data, TEST_DATA_SIZE);
    
    // 生成 ZUC 密钥
    unsigned char key[ZUC_KEY_SIZE];
    if (rand_bytes(key, ZUC_KEY_SIZE) != 1) {
        print_test_result("ZUC 密钥生成", 0);
        return 0;
    }
    
    // 加密
    unsigned char encrypted[TEST_DATA_SIZE];
    unsigned char decrypted[TEST_DATA_SIZE];
    unsigned char iv[16] = {0};
    
    ZUC_STATE state;
    zuc_init(&state, key, iv);
    zuc_encrypt(&state, test_data, TEST_DATA_SIZE, encrypted);
    
    // 解密
    zuc_init(&state, key, iv);
    zuc_encrypt(&state, encrypted, TEST_DATA_SIZE, decrypted);
    
    // 验证解密结果
    int decryption_correct = compare_data(test_data, decrypted, TEST_DATA_SIZE);
    print_test_result("ZUC 加密解密", decryption_correct);
    
    return decryption_correct;
}

// 测试4: 文件加密解密
int test_file_encryption() {
    print_test_header("文件加密解密测试");
    
    const char *input_file = "test_input.txt";
    const char *encrypted_file = "test_encrypted.zuc";
    const char *decrypted_file = "test_decrypted.txt";
    const char *key_file = "test_zuc.key";
    
    // 清理旧文件
    unlink(input_file); unlink(encrypted_file);
    unlink(decrypted_file); unlink(key_file);
    
    // 创建测试文件
    FILE *fp = fopen(input_file, "wb");
    if (!fp) {
        print_test_result("测试文件创建", 0);
        return 0;
    }
    
    unsigned char test_data[TEST_DATA_SIZE];
    generate_test_data(test_data, TEST_DATA_SIZE);
    fwrite(test_data, 1, TEST_DATA_SIZE, fp);
    fclose(fp);
    
    // 生成密钥并加密
    unsigned char key[ZUC_KEY_SIZE];
    if (rand_bytes(key, ZUC_KEY_SIZE) != 1) {
        print_test_result("密钥生成", 0);
        return 0;
    }
    
    // 读取输入文件
    fp = fopen(input_file, "rb");
    if (!fp) {
        print_test_result("输入文件读取", 0);
        return 0;
    }
    
    fseek(fp, 0, SEEK_END);
    size_t file_size = ftell(fp);
    rewind(fp);
    
    unsigned char *input_data = malloc(file_size);
    fread(input_data, 1, file_size, fp);
    fclose(fp);
    
    // 加密
    unsigned char *encrypted_data = malloc(file_size);
    unsigned char iv[16] = {0};
    ZUC_STATE state;
    zuc_init(&state, key, iv);
    zuc_encrypt(&state, input_data, file_size, encrypted_data);
    
    // 保存加密文件和密钥
    fp = fopen(encrypted_file, "wb");
    fwrite(encrypted_data, 1, file_size, fp);
    fclose(fp);
    
    fp = fopen(key_file, "wb");
    fwrite(key, 1, ZUC_KEY_SIZE, fp);
    fclose(fp);
    
    // 解密
    unsigned char *decrypted_data = malloc(file_size);
    zuc_init(&state, key, iv);
    zuc_encrypt(&state, encrypted_data, file_size, decrypted_data);
    
    // 保存解密文件
    fp = fopen(decrypted_file, "wb");
    fwrite(decrypted_data, 1, file_size, fp);
    fclose(fp);
    
    // 验证解密结果
    int file_decryption_correct = compare_data(input_data, decrypted_data, file_size);
    print_test_result("文件加密解密", file_decryption_correct);
    
    // 清理内存
    free(input_data);
    free(encrypted_data);
    free(decrypted_data);
    
    return file_decryption_correct;
}

// 测试5: 端到端测试
int test_end_to_end() {
    print_test_header("端到端测试");
    
    const char *message = "Hello, SM2 ECDH and ZUC encryption!";
    const char *alice_priv = "e2e_alice_priv.pem";
    const char *alice_pub = "e2e_alice_pub.pem";
    const char *bob_priv = "e2e_bob_priv.pem";
    const char *bob_pub = "e2e_bob_pub.pem";
    const char *session_key = "e2e_session.key";
    const char *encrypted_file = "e2e_encrypted.zuc";
    const char *decrypted_file = "e2e_decrypted.txt";
    
    // 清理旧文件
    unlink(alice_priv); unlink(alice_pub);
    unlink(bob_priv); unlink(bob_pub);
    unlink(session_key); unlink(encrypted_file); unlink(decrypted_file);
    
    // 1. 生成密钥对
    if (sm2_generate_keypair(alice_priv, alice_pub) != 0 ||
        sm2_generate_keypair(bob_priv, bob_pub) != 0) {
        print_test_result("端到端密钥生成", 0);
        return 0;
    }
    
    // 2. 密钥协商
    if (sm2_derive_session_key(alice_priv, bob_pub, session_key) != 0) {
        print_test_result("端到端密钥协商", 0);
        return 0;
    }
    
    // 3. 读取会话密钥
    FILE *fp = fopen(session_key, "rb");
    if (!fp) {
        print_test_result("会话密钥读取", 0);
        return 0;
    }
    
    unsigned char key[64];
    size_t key_size = fread(key, 1, 64, fp);
    fclose(fp);
    
    if (key_size != 64) {
        print_test_result("会话密钥长度", 0);
        return 0;
    }
    
    // 4. 使用会话密钥加密消息
    size_t msg_len = strlen(message);
    unsigned char *encrypted = malloc(msg_len);
    unsigned char iv[16] = {0};
    
    ZUC_STATE state;
    zuc_init(&state, key, iv);
    zuc_encrypt(&state, (unsigned char*)message, msg_len, encrypted);
    
    // 保存加密文件
    fp = fopen(encrypted_file, "wb");
    fwrite(encrypted, 1, msg_len, fp);
    fclose(fp);
    
    // 5. 解密消息
    unsigned char *decrypted = malloc(msg_len);
    zuc_init(&state, key, iv);
    zuc_encrypt(&state, encrypted, msg_len, decrypted);
    
    // 保存解密文件
    fp = fopen(decrypted_file, "wb");
    fwrite(decrypted, 1, msg_len, fp);
    fclose(fp);
    
    // 6. 验证解密结果
    int e2e_correct = compare_data((unsigned char*)message, decrypted, msg_len);
    print_test_result("端到端加密解密", e2e_correct);
    
    // 清理内存
    free(encrypted);
    free(decrypted);
    
    return e2e_correct;
}

// 清理测试文件
void cleanup_test_files() {
    const char *files[] = {
        "test_priv.pem", "test_pub.pem",
        "alice_priv.pem", "alice_pub.pem", "alice_session.key",
        "bob_priv.pem", "bob_pub.pem", "bob_session.key",
        "test_input.txt", "test_encrypted.zuc", "test_decrypted.txt", "test_zuc.key",
        "e2e_alice_priv.pem", "e2e_alice_pub.pem",
        "e2e_bob_priv.pem", "e2e_bob_pub.pem",
        "e2e_session.key", "e2e_encrypted.zuc", "e2e_decrypted.txt"
    };
    
    for (int i = 0; i < sizeof(files)/sizeof(files[0]); i++) {
        unlink(files[i]);
    }
}

int main() {
    printf("%s=== SM2 ECDH + ZUC 加密测试程序 ===%s\n", COLOR_BLUE, COLOR_RESET);
    printf("测试时间: %s\n", __DATE__);
    
    // 初始化随机数种子
    srand(time(NULL));
    
    // 运行所有测试
    test_sm2_key_generation();
    test_sm2_ecdh();
    test_zuc_encryption();
    test_file_encryption();
    test_end_to_end();
    
    // 打印最终统计
    print_final_stats();
    
    // 清理测试文件
    cleanup_test_files();
    
    return (stats.failed_tests == 0) ? 0 : 1;
} 
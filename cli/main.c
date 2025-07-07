// main.c
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <gmssl/zuc.h>
#include <gmssl/rand.h>
#include "sm2_ecdh.h"

#define COLOR_GREEN  "\033[1;32m"
#define COLOR_RED    "\033[1;31m"
#define COLOR_YELLOW "\033[1;33m"
#define COLOR_RESET  "\033[0m"

#define ZUC_KEY_SIZE 16 // 128-bit

// 命令行参数结构
typedef struct {
    const char *infile;
    const char *outfile;
    const char *keyfile;
    const char *privkey;
    const char *pubkey;
    const char *peer_pubkey;
} cmd_args_t;

// 函数声明
void print_usage(const char *prog);
int read_file(const char *filename, unsigned char **data, size_t *len);
int write_file(const char *filename, const unsigned char *data, size_t len);
int parse_encrypt_args(int argc, char **argv, cmd_args_t *args);
int parse_decrypt_args(int argc, char **argv, cmd_args_t *args);
int parse_gen_keys_args(int argc, char **argv, cmd_args_t *args);
int parse_key_exchange_args(int argc, char **argv, cmd_args_t *args);
int handle_encrypt(const cmd_args_t *args);
int handle_decrypt(const cmd_args_t *args);
int handle_gen_keys(const cmd_args_t *args);
int handle_key_exchange(const cmd_args_t *args);

// 打印使用说明
void print_usage(const char *prog) {
    printf("Usage:\n");
    printf("  %s encrypt -in <input.txt> -out <output.zuc>\n", prog);
    printf("  %s decrypt -in <input.zuc> -out <output.txt> -key <zuc.key>\n", prog);
    printf("  %s gen-keys -priv <priv.pem> -pub <pub.pem>\n", prog);
    printf("  %s key-exchange -priv <my.pem> -peer <peer_pub.pem> -out <session.key>\n", prog);
}

// 读取文件
int read_file(const char *filename, unsigned char **data, size_t *len) {
    FILE *fp = fopen(filename, "rb");
    if (!fp) {
        fprintf(stderr, COLOR_RED "[-] Cannot open file: %s\n" COLOR_RESET, filename);
        return -1;
    }
    
    fseek(fp, 0, SEEK_END);
    *len = ftell(fp);
    rewind(fp);
    
    *data = malloc(*len);
    if (!*data) {
        fclose(fp);
        return -1;
    }
    
    fread(*data, 1, *len, fp);
    fclose(fp);
    return 0;
}

// 写入文件
int write_file(const char *filename, const unsigned char *data, size_t len) {
    FILE *fp = fopen(filename, "wb");
    if (!fp) {
        fprintf(stderr, COLOR_RED "[-] Cannot write file: %s\n" COLOR_RESET, filename);
        return -1;
    }
    
    fwrite(data, 1, len, fp);
    fclose(fp);
    return 0;
}

// 解析加密命令参数
int parse_encrypt_args(int argc, char **argv, cmd_args_t *args) {
    memset(args, 0, sizeof(cmd_args_t));
    
    for (int i = 2; i < argc; i++) {
        if (strcmp(argv[i], "-in") == 0 && i + 1 < argc) {
            args->infile = argv[++i];
        } else if (strcmp(argv[i], "-out") == 0 && i + 1 < argc) {
            args->outfile = argv[++i];
        }
    }
    
    if (!args->infile || !args->outfile) {
        fprintf(stderr, COLOR_RED "[-] Missing required arguments for encrypt\n" COLOR_RESET);
        return -1;
    }
    
    return 0;
}

// 解析解密命令参数
int parse_decrypt_args(int argc, char **argv, cmd_args_t *args) {
    memset(args, 0, sizeof(cmd_args_t));
    
    for (int i = 2; i < argc; i++) {
        if (strcmp(argv[i], "-in") == 0 && i + 1 < argc) {
            args->infile = argv[++i];
        } else if (strcmp(argv[i], "-out") == 0 && i + 1 < argc) {
            args->outfile = argv[++i];
        } else if (strcmp(argv[i], "-key") == 0 && i + 1 < argc) {
            args->keyfile = argv[++i];
        }
    }
    
    if (!args->infile || !args->outfile || !args->keyfile) {
        fprintf(stderr, COLOR_RED "[-] Missing required arguments for decrypt\n" COLOR_RESET);
        return -1;
    }
    
    return 0;
}

// 解析生成密钥对命令参数
int parse_gen_keys_args(int argc, char **argv, cmd_args_t *args) {
    memset(args, 0, sizeof(cmd_args_t));
    
    for (int i = 2; i < argc; i++) {
        if (strcmp(argv[i], "-priv") == 0 && i + 1 < argc) {
            args->privkey = argv[++i];
        } else if (strcmp(argv[i], "-pub") == 0 && i + 1 < argc) {
            args->pubkey = argv[++i];
        }
    }
    
    if (!args->privkey || !args->pubkey) {
        fprintf(stderr, COLOR_RED "[-] Missing required arguments for gen-keys\n" COLOR_RESET);
        return -1;
    }
    
    return 0;
}

// 解析密钥交换命令参数
int parse_key_exchange_args(int argc, char **argv, cmd_args_t *args) {
    memset(args, 0, sizeof(cmd_args_t));
    
    for (int i = 2; i < argc; i++) {
        if (strcmp(argv[i], "-priv") == 0 && i + 1 < argc) {
            args->privkey = argv[++i];
        } else if (strcmp(argv[i], "-peer") == 0 && i + 1 < argc) {
            args->peer_pubkey = argv[++i];
        } else if (strcmp(argv[i], "-out") == 0 && i + 1 < argc) {
            args->outfile = argv[++i];
        }
    }
    
    if (!args->privkey || !args->peer_pubkey || !args->outfile) {
        fprintf(stderr, COLOR_RED "[-] Missing required arguments for key-exchange\n" COLOR_RESET);
        return -1;
    }
    
    return 0;
}

// 处理加密
int handle_encrypt(const cmd_args_t *args) {
    unsigned char *in_data = NULL;
    size_t in_len = 0;
    
    // 读取输入文件
    if (read_file(args->infile, &in_data, &in_len) != 0) {
        return -1;
    }
    
    // 生成随机密钥
    unsigned char key[ZUC_KEY_SIZE];
    if (rand_bytes(key, ZUC_KEY_SIZE) != 1) {
        fprintf(stderr, COLOR_RED "[-] Failed to generate random ZUC key\n" COLOR_RESET);
        free(in_data);
        return -1;
    }
    
    // 加密
    unsigned char out_data[in_len];
    unsigned char iv[16] = {0}; // 固定 IV（全 0）
    
    ZUC_STATE state;
    zuc_init(&state, key, iv);
    zuc_encrypt(&state, in_data, in_len, out_data);
    
    // 写入输出文件
    if (write_file(args->outfile, out_data, in_len) != 0) {
        free(in_data);
        return -1;
    }
    
    // 保存密钥
    if (write_file("zuc.key", key, ZUC_KEY_SIZE) != 0) {
        free(in_data);
        return -1;
    }
    
    // 输出结果
    printf(COLOR_GREEN "[+] Encryption successful\n" COLOR_RESET);
    printf(COLOR_YELLOW "[+] Encrypted file: %s\n" COLOR_RESET, args->outfile);
    printf(COLOR_YELLOW "[+] Key saved to: zuc.key\n" COLOR_RESET);
    
    free(in_data);
    return 0;
}

// 处理解密
int handle_decrypt(const cmd_args_t *args) {
    unsigned char *in_data = NULL;
    size_t in_len = 0;
    unsigned char *key = NULL;
    size_t key_len = 0;
    
    // 读取输入文件
    if (read_file(args->infile, &in_data, &in_len) != 0) {
        return -1;
    }
    
    // 读取密钥文件
    if (read_file(args->keyfile, &key, &key_len) != 0 || key_len != ZUC_KEY_SIZE) {
        fprintf(stderr, COLOR_RED "[-] Invalid key file\n" COLOR_RESET);
        free(in_data);
        return -1;
    }
    
    // 解密
    unsigned char out_data[in_len];
    unsigned char iv[16] = {0}; // 固定 IV（全 0）
    
    ZUC_STATE state;
    zuc_init(&state, key, iv);
    zuc_encrypt(&state, in_data, in_len, out_data); // 解密
    
    // 写入输出文件
    if (write_file(args->outfile, out_data, in_len) != 0) {
        free(in_data);
        free(key);
        return -1;
    }
    
    // 输出结果
    printf(COLOR_GREEN "[+] Decryption successful\n" COLOR_RESET);
    printf(COLOR_YELLOW "[+] Decrypted file: %s\n" COLOR_RESET, args->outfile);
    printf(COLOR_YELLOW "[+] Preview:\n" COLOR_RESET);
    fwrite(out_data, 1, in_len < 512 ? in_len : 512, stdout);
    printf("\n");
    
    free(in_data);
    free(key);
    return 0;
}

// 处理生成密钥对
int handle_gen_keys(const cmd_args_t *args) {
    if (sm2_generate_keypair(args->privkey, args->pubkey) == 0) {
        printf(COLOR_GREEN "[+] SM2 keypair generated:\n" COLOR_RESET);
        printf("    Private: %s\n", args->privkey);
        printf("    Public : %s\n", args->pubkey);
        return 0;
    } else {
        fprintf(stderr, COLOR_RED "[-] Failed to generate SM2 keypair\n" COLOR_RESET);
        return -1;
    }
}

// 处理密钥交换
int handle_key_exchange(const cmd_args_t *args) {
    if (sm2_derive_session_key(args->privkey, args->peer_pubkey, args->outfile) == 0) {
        printf(COLOR_GREEN "[+] Session key derived successfully:\n" COLOR_RESET);
        printf("    Saved to: %s\n", args->outfile);
        return 0;
    } else {
        fprintf(stderr, COLOR_RED "[-] Failed to derive session key\n" COLOR_RESET);
        return -1;
    }
}

// 主函数
int main(int argc, char **argv) {
    if (argc < 2) {
        print_usage(argv[0]);
        return 1;
    }
    
    const char *mode = argv[1];
    cmd_args_t args;
    
    if (strcmp(mode, "encrypt") == 0) {
        if (argc < 5) {
            print_usage(argv[0]);
            return 1;
        }
        
        if (parse_encrypt_args(argc, argv, &args) != 0) {
            print_usage(argv[0]);
            return 1;
        }
        
        if (handle_encrypt(&args) != 0) {
            return 1;
        }
        
    } else if (strcmp(mode, "decrypt") == 0) {
        if (argc < 6) {
            print_usage(argv[0]);
            return 1;
        }
        
        if (parse_decrypt_args(argc, argv, &args) != 0) {
            print_usage(argv[0]);
            return 1;
        }
        
        if (handle_decrypt(&args) != 0) {
            return 1;
        }
        
    } else if (strcmp(mode, "gen-keys") == 0) {
        if (argc < 5) {
            print_usage(argv[0]);
            return 1;
        }
        
        if (parse_gen_keys_args(argc, argv, &args) != 0) {
            print_usage(argv[0]);
            return 1;
        }
        
        if (handle_gen_keys(&args) != 0) {
            return 1;
        }
        
    } else if (strcmp(mode, "key-exchange") == 0) {
        if (argc < 7) {
            print_usage(argv[0]);
            return 1;
        }
        
        if (parse_key_exchange_args(argc, argv, &args) != 0) {
            print_usage(argv[0]);
            return 1;
        }
        
        if (handle_key_exchange(&args) != 0) {
            return 1;
        }
        
    } else {
        fprintf(stderr, COLOR_RED "[-] Unknown mode: %s\n" COLOR_RESET, mode);
        print_usage(argv[0]);
        return 1;
    }
    
    return 0;
}

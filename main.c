// main.c
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <gmssl/zuc.h>
#include <gmssl/rand.h>

#define COLOR_GREEN  "\033[1;32m"
#define COLOR_RED    "\033[1;31m"
#define COLOR_YELLOW "\033[1;33m"
#define COLOR_RESET  "\033[0m"

#define ZUC_KEY_SIZE 16 // 128-bit

void print_usage(const char *prog) {
    printf("Usage:\n");
    printf("  %s encrypt -in <input.txt> -out <output.zuc>\n", prog);
    printf("  %s decrypt -in <input.zuc> -out <output.txt> -key <zuc.key>\n", prog);
}

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

int main(int argc, char **argv) {
    if (argc < 5) {
        print_usage(argv[0]);
        return 1;
    }

    const char *mode = argv[1];
    const char *infile = NULL;
    const char *outfile = NULL;
    const char *keyfile = NULL;

    for (int i = 2; i < argc; i++) {
        if (strcmp(argv[i], "-in") == 0) infile = argv[++i];
        else if (strcmp(argv[i], "-out") == 0) outfile = argv[++i];
        else if (strcmp(argv[i], "-key") == 0) keyfile = argv[++i];
    }

    if (!infile || !outfile) {
        print_usage(argv[0]);
        return 1;
    }

    unsigned char *in_data = NULL;
    size_t in_len = 0;
    if (read_file(infile, &in_data, &in_len) != 0) {
        return 1;
    }

    unsigned char out_data[in_len];
    unsigned char iv[16] = {0}; // 固定 IV（全 0）

    if (strcmp(mode, "encrypt") == 0) {
        unsigned char key[ZUC_KEY_SIZE];
        if (rand_bytes(key, ZUC_KEY_SIZE) != 1) {
            fprintf(stderr, COLOR_RED "[-] Failed to generate random ZUC key\n" COLOR_RESET);
            return 1;
        }

        ZUC_STATE state;
        zuc_init(&state, key, iv);
        zuc_encrypt(&state, in_data, in_len, out_data);

        if (write_file(outfile, out_data, in_len) != 0) return 1;
        if (write_file("zuc.key", key, ZUC_KEY_SIZE) != 0) return 1;

        printf(COLOR_GREEN "[+] Encryption successful\n" COLOR_RESET);
        printf(COLOR_YELLOW "[+] Encrypted file: %s\n" COLOR_RESET, outfile);
        printf(COLOR_YELLOW "[+] Key saved to: zuc.key\n" COLOR_RESET);
    }
    else if (strcmp(mode, "decrypt") == 0) {
        if (!keyfile) {
            fprintf(stderr, COLOR_RED "[-] Please provide -key <zuc.key> for decryption\n" COLOR_RESET);
            return 1;
        }

        unsigned char *key = NULL;
        size_t key_len = 0;
        if (read_file(keyfile, &key, &key_len) != 0 || key_len != ZUC_KEY_SIZE) {
            fprintf(stderr, COLOR_RED "[-] Invalid key file\n" COLOR_RESET);
            return 1;
        }

        ZUC_STATE state;
        zuc_init(&state, key, iv);
        zuc_encrypt(&state, in_data, in_len, out_data); // 解密

        if (write_file(outfile, out_data, in_len) != 0) return 1;

        printf(COLOR_GREEN "[+] Decryption successful\n" COLOR_RESET);
        printf(COLOR_YELLOW "[+] Decrypted file: %s\n" COLOR_RESET, outfile);
        printf(COLOR_YELLOW "[+] Preview:\n" COLOR_RESET);
        fwrite(out_data, 1, in_len < 512 ? in_len : 512, stdout);
        printf("\n");
        free(key);
    }
    else {
        print_usage(argv[0]);
        return 1;
    }

    free(in_data);
    return 0;
}

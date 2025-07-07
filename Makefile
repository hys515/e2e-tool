CC = gcc
CFLAGS = -Iinclude -I/usr/local/include -Wall
LDFLAGS = /usr/local/lib/libgmssl.a -framework Security
TARGET = e2e-tool
TEST_TARGET = test_sm2_ecdh

SRCS = cli/main.c src/sm2_ecdh.c
OBJS = $(SRCS:.c=.o)
TEST_SRCS = test_sm2_ecdh.c src/sm2_ecdh.c
TEST_OBJS = $(TEST_SRCS:.c=.o)

all: $(TARGET)

test: $(TEST_TARGET)

$(TARGET): $(OBJS)
	$(CC) -o $@ $^ $(LDFLAGS)

$(TEST_TARGET): $(TEST_OBJS)
	$(CC) -o $@ $^ $(LDFLAGS)

clean:
	rm -f $(TARGET) $(TEST_TARGET) $(OBJS) $(TEST_OBJS)

.PHONY: all test clean

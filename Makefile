CC = gcc
CFLAGS = -Iinclude -I/usr/local/include -Wall
LDFLAGS = /usr/local/lib/libgmssl.a -framework Security
TARGET = e2e-tool

SRCS = cli/main.c src/sm2_ecdh.c
OBJS = $(SRCS:.c=.o)

all: $(TARGET)

$(TARGET): $(OBJS)
	$(CC) -o $@ $^ $(LDFLAGS)

clean:
	rm -f $(TARGET) $(OBJS)

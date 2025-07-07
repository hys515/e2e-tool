CC = gcc
CFLAGS = -I/usr/local/include
LDFLAGS = /usr/local/lib/libgmssl.a -framework Security
TARGET = e2e-tool

SRCS = main.c
OBJS = $(SRCS:.c=.o)

all: $(TARGET)

$(TARGET): $(OBJS)
	$(CC) -o $@ $^ $(LDFLAGS)

clean:
	rm -f $(TARGET) *.o

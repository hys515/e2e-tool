CC = gcc
CFLAGS = -Iinclude -Wall
LDFLAGS = -lgmssl

SRC = cli/main.c src/sm2_ecdh.c
OBJ = $(SRC:.c=.o)
TARGET = e2e-tool

all: $(TARGET)

$(TARGET): $(OBJ)
	$(CC) -o $@ $^ $(LDFLAGS)

clean:
	rm -f $(OBJ) $(TARGET)

BINS = read-temp

# Flag values are based on the original Makefile in the 'examples' directory of
# the wiringPi distribution.
DEBUG = -O3
CC = gcc
INCLUDE = -I/usr/local/include
CFLAGS = $(DEBUG) -Wall $(INCLUDE) -Winline -pipe
LDFLAGS	= -L/usr/local/lib
LDLIBS = -lwiringPi

all: $(BINS)

clean:
	rm -f $(BINS)

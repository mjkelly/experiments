# Skeleton Makefile to add wiringPi libraries at link time.
# GNU Make has some implicit rules to handle actually building the binaries.
#
# Flag values are based on the original Makefile in the 'examples' directory of
# the wiringPi distribution. wiringPi is here:
# https://projects.drogon.net/raspberry-pi/wiringpi/

DEBUG = -O3
CC = gcc
INCLUDE = -I/usr/local/include
CFLAGS = $(DEBUG) -Wall $(INCLUDE) -Winline -pipe

LDFLAGS	= -L/usr/local/lib
LDLIBS = -lwiringPi -lpthread -lm

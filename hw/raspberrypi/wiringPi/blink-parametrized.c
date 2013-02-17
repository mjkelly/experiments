/*
 * blink.c:
 *	Standard "blink" program in wiringPi. Blinks an LED connected
 *	to the first GPIO pin.
 * 
 *
 * This version is modified to take the delay in ms as a parameter.
 *
 *
 * Copyright (c) 2012-2013 Gordon Henderson. <projects@drogon.net>
 ***********************************************************************
 * This file is part of wiringPi:
 *	https://projects.drogon.net/raspberry-pi/wiringpi/
 *
 *    wiringPi is free software: you can redistribute it and/or modify
 *    it under the terms of the GNU Lesser General Public License as published by
 *    the Free Software Foundation, either version 3 of the License, or
 *    (at your option) any later version.
 *
 *    wiringPi is distributed in the hope that it will be useful,
 *    but WITHOUT ANY WARRANTY; without even the implied warranty of
 *    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 *    GNU Lesser General Public License for more details.
 *
 *    You should have received a copy of the GNU Lesser General Public License
 *    along with wiringPi.  If not, see <http://www.gnu.org/licenses/>.
 ***********************************************************************
 */

#include <stdlib.h>
#include <stdio.h>
#include <wiringPi.h>

// LED Pin - wiringPi pin 0 is BCM_GPIO 17.

#define	LED	0

void usage(char* name) {
  fprintf(stderr, "Usage: %s DELAY_IN_MS\n", name);
  exit(2);
}

int main (int argc, char** argv) {
  int delay_ms = 500;
  if (argc < 2) {
    usage(argv[0]);
  }

  delay_ms = atoi(argv[1]);
  printf("Raspberry Pi blink, delay_ms = %d\n", delay_ms);

  if (wiringPiSetup () == -1)
    return 1;

  pinMode(LED, OUTPUT);

  for (;;) {
    digitalWrite(LED, 1);
    delay (delay_ms);
    digitalWrite(LED, 0);
    delay (delay_ms);
  }
  return 0;
}

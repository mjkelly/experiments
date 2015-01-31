/* Read the current temperature from a TMP36 thermistor connected via an
 * MCP3008 analog-to-digital converter to a Raspberry Pi. We use the SPI module
 * and wiringPi to read from the MCP3008.
 *
 * TMP36: http://www.ladyada.net/learn/sensors/temp36.html
 * MCP3008: https://www.adafruit.com/products/856
 * (There is a howto on connecting the TMP36 and MCP3008 to a rasperry pi, but
 * it does not use the SPI kernel module -- so note that this setup is a bit
 * different.)
 *
 * More info on SPI: https://en.wikipedia.org/wiki/Serial_Peripheral_Interface_Bus
 */

#include <errno.h>
#include <getopt.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include <wiringPi.h>
#include <mcp3004.h>

/* Where to start numbering the SPI pins. After inserting the mcp3004 module,
 * we will be able to do analog reads from pin 100. */
#define SPI_BASE_PIN 100
/* We have 2 channels to choose from on the raspberry pi. Our MCP3004 is
 * connected to the CE0, which is SPI channel 0. */
#define SPI_CHAN 0

#define OPT_SPEC "vh"
void usage(char * name) {
  fprintf(stderr,
      "Usage: %s [-v]\n\n"
      "Outputs temperature in celsius, as read from a TMP36 attached to an\n"
      "MCP3008 A/D converter.\n\n"
      "With -v, outputs summary (value read, plus intermediate values).\n",
      name);
  exit(2);
}

/* Converts the digital value we read from the MCP3008 into millivolts.
 *
 * Based on Equation 4-2 on this datasheet
 * <http://www.adafruit.com/datasheets/MCP3008.pdf>, the digital output is:
 * Vref / 1024.
 *
 * We are connected to the +3.3V pin on the raspberry pi, so our Vref is 3300mV
 * (3.3V).
 */
double dOutToMillivolts(int dOut) {
  const double Vref = 3300.0;
  return ((double) dOut) * (Vref / 1024.0);
}

/* Converts a millivolt value from the TMP36 sensor into celsius.
 *
 * From http://www.ladyada.net/learn/sensors/temp36.html:
 * Temp in °C = [(Vout in mV) - 500] / 10
 */
double millivoltsToCelsius(double mv) {
  return (mv - 500.0) / 10.0;
}

/* Converts celsius values to fahrenheit, for Americans. */
double celsiusToFahrenheit(double celsius) {
   return (celsius * 9.0 / 5.0) + 32.0;
}

int main (int argc, char** argv) {
  int c;
  char verbose = 0;

  while ((c = getopt (argc, argv, OPT_SPEC)) != -1) {
    switch (c) {
    case 'v':
      verbose = 1;
      break;
    case 'h':
      usage(argv[0]);
      break;
    default:
      usage(argv[0]);
      break;
    }
  }

  if (wiringPiSetup () < 0) {
    fprintf(stderr, "Error in wiringPiSetup: %s", strerror(errno));
    return -1;
  }
  if (mcp3004Setup(SPI_BASE_PIN, SPI_CHAN) < 0) {
    fprintf(stderr, "Error in mcp3004Setup: %s", strerror(errno));
    return -1;
  }

  int dOut = analogRead(SPI_BASE_PIN);
  double mv = dOutToMillivolts(dOut);
  double tempC = millivoltsToCelsius(mv);

  if (verbose) {
    double tempF = celsiusToFahrenheit(tempC);
    printf("digital_value = %d\n", dOut);
    printf("mV = %f\n", mv);
    printf("temp_C = %.1f\n", tempC);
    printf("temp_F = %.1f\n", tempF);
  } else {
    printf("%.1f\n", tempC);
  }

  return 0;
}

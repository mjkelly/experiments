# wiringPi Temperature Sensor

These are a set of programs for collecting temperature from a TMP36 temperature sensor whose voltage is fed to an MCP3008 analog to digital converter. We read the values via SPI using the mcp3004 extension in wiringPi (<http://wiringpi.com/>).

The programs are:
* `read-temp.c`: This reads the values via SPI and prints them out. For non-interactive use, this can be run as a cronjob.
* `prometheus-exporter.py`: This exports temperature data that it finds in a file in a format that can be scraped by the Prometheus (<http://prometheus.io>) monitoring system. It also serves a simple text-only display.

There could easily be other exporters for other monitoring systems.

## Requirements
Most importantly, you must have a TMP36 and MCP3008 connected to your raspberry pi. I used the wiring described in this project, <http://hertaville.com/2013/07/24/interfacing-an-spi-adc-mcp3008-chip-to-the-raspberry-pi-using-c/>. (The "CS0" pin in the wiring diagram for that project was labelled "CE0" on my raspberry pi's cobbler breakout board.)

wiringPi should be installed, and you should install the SPI kernel module, `spi_bcm2708`. Run:

    modprobe spi_bcm2708
    
On Raspbian, you also must remove the kernel module from the black list by removing the "spi_bcm2708" line from `/etc/modprobe.d/raspi-blacklist.conf`.

This is described in more detail here: <https://projects.drogon.net/understanding-spi-on-the-raspberry-pi/>.

I tested the physical setup by hooking up a potentiometer where the temperature sensor would be and reading values using the `gpio` program included with wiringPi:

    gpio load spi
    gpio -x mcp3004:1000:0 aread 1000

This loads the `mcp3004` extension, selects SPI channel 0, connects it to wiringPi's pin 1000, then reads from pin 1000. 

## Installation
Note that there's a fair bit of physical setup required before installing the software is useful; see the "Requirements" section below.

Compile all C programs in this directory by running `make`. The easiest way to trigger these programs is to run them from root's crontab. Put these lines in your crontab (via `crontab -e`, etc):

    * * * * * ~/read-temp > /var/run/current_temp_c
    @reboot ~/prometheus-exporter.py >/dev/null 2>&1 &

This will run read-temp every minute and send its output to `/var/run/current_temp_c`. When the machine starts, prometheus-exporter will start. By default it will put its web interface on port 8080, and read from `/var/run/current_temp_c`.

To kick off prometheus-exporter without rebooting, just run the second line in the crontab: `~/prometheus-exporter.py >/dev/null 2>&1 &`.

Go to http://<your raspberry pi's IP address>:8080 and check that you see text. You will have to wait about 1 minute after installing the cronab before getting up-to-date temperature information.

Yay!

## References
  * AdaFruit has a nice introduction to using temperature sensors here, <http://www.ladyada.net/learn/sensors/temp36.html>, which includes most of what I needed to know about the TMP36.
  * This is the TMP36 datasheet: <http://www.analog.com/static/imported-files/data_sheets/TMP35_36_37.pdf>
  * This is the MCP3008 datasheet: <http://www.adafruit.com/datasheets/MCP3008.pdf>
  * SPI: <https://en.wikipedia.org/wiki/Serial_Peripheral_Interface_Bus>.


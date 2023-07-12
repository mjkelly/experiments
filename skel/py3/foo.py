#!/usr/bin/python3
# -----------------------------------------------------------------
# foo.py --
#
# Copyright 2020 Michael Kelly (michael@michaelkelly.org)
#
# Sat Apr 18 14:54:50 EDT 2020
# -----------------------------------------------------------------

import click
import logging

# Format inspired by glog
logging.basicConfig(
    format='%(levelname)s %(asctime)s %(filename)s:%(lineno)d %(message)s')
logger = logging.getLogger()


@click.command()
@click.option(
    "--log-level",
    type=click.Choice(["CRITICAL", "ERROR", "WARNING", "INFO", "DEBUG"]),
    default="INFO",
    show_default=True,
    callback=lambda ctx, param, val: logger.setLevel(val),
    expose_value=False,
    help="Set the log level")
def main():
    """Does some stuff.

    Examples:

    \b
    Do thing:
        ./foo.py
    """
    logger.info("Hello")


if __name__ == "__main__":
    main()

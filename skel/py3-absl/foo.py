#!/usr/bin/python3
# -----------------------------------------------------------------
# foo.py --
#
# Copyright 2020 Michael Kelly (michael@michaelkelly.org)
#
# Sat Apr 18 14:54:50 EDT 2020
# -----------------------------------------------------------------

import sys

from absl import app
from absl import flags
from absl import logging

FLAGS = flags.FLAGS

flags.DEFINE_string('echo', None, 'Text to echo.')


def main(argv):
  del argv  # Unused.

  print('Running under Python {0[0]}.{0[1]}.{0[2]}'.format(sys.version_info),
        file=sys.stderr)
  logging.info('echo is %s.', FLAGS.echo)


if __name__ == '__main__':
  app.run(main)

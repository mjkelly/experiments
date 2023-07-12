#!/usr/bin/python
# -----------------------------------------------------------------
# untar.py -- Untar tarballs while protecting against tarbombs.
# Copyright 2011 Michael Kelly (michael@michaelkelly.org)
#
# Sample usage:
# $ untar.py tarfile.tar
# -> untars tarfile.tar as normal
#    (if tarfile.tar is a tarbomb and creates multiple files in the current
#    directory, all files are expanded to a new directory 'tarfile')
#
# $ untar.py -v tarfile.tar
# -> untars tarfile.tar, passing -v (verbose) to tar
#
# $ untar.py -j tarbomb.tbz2
# -> Expands and untars tarfile.tbz2 to current directory (or 'tarfile' if
#    necessary). If your tar auto-detects tarred+compressed files and
#    auto-expands them, then you shouldn't actually need to do this.
#
# untar.py always passes '-x', '-f', and '-C FILE' to tar, so passing them
# explicitly doesn't make any sense.
#
# Tested with: tar (GNU tar) 1.23
#
# Sat Oct 29 22:01:23 EDT 2011
# -----------------------------------------------------------------

import os
import re
import subprocess
import sys

_TAR = '/bin/tar'

def tar_list(tar_file):
  """Returns a list of all files in the given tar file.

  Returns: ([str], str) A tuple of the list of files (or None) and any stderr
           output from tar.
  """
  proc = subprocess.Popen([_TAR, '-tf', tar_file],
                          stdout=subprocess.PIPE, stderr=subprocess.PIPE)
  stdout, stderr = proc.communicate()
  if proc.returncode:
    return (None, stderr)
  else:
    return (stdout.strip().split('\n'), stderr)


def base_directories(paths):
  """Given a list of paths, returns the first directory component (or the
  filename, if there is none) of each.
  """
  dirs = set()
  for path in paths:
    # We need to account for absolute paths
    if path.startswith(os.sep):
      dirs.add(os.sep + path.split(os.sep, 2)[1])
    else:
      dirs.add(path.split(os.sep, 1)[0])
  return dirs


def archive_name(archive_path):
  """Make a guess at the archive name based on its name without a suffix."""
  base = os.path.basename(archive_path)
  return re.sub(r'\.(tar|tar\.\w+|tgz|tbz2)$', '', base, 1)


def untar(tar_file, extra_args, directory):
  """Untars a file.

  Args:
    extra_args: [str] Extra args to add, before the filename.
    directory: (str) Untar into the given dirctory. If None, use the
               CWD.
  Returns:
    exit code from tar
  """
  cmd = [_TAR] + extra_args + ['-xf', tar_file]
  if directory is not None:
    cmd += ['-C', directory]
  proc = subprocess.Popen(cmd)
  proc.communicate()
  return proc.returncode


def usage():
  usage_str = ('Usage: %s [FLAGS] TARFILE\n\n'
               'Untars TARFILE to a subdirectory of the CWD. If the TARFILE\n'
               'will naturally expand only to a single subdirecory, that one\n'
               'is used. Otherwise, the name of the directory without a\n'
               'suffix is used.\n\n'
               'Any FLAGS are passed straight to tar.' % sys.argv[0])
  print >>sys.stderr, usage_str


def error(msg):
  print >>sys.stderr, '%s: %s' % (sys.argv[0], msg)


def main(argv):
  if len(argv) < 2:
    usage()
    return 2
  tar_file = argv[-1]
  flags = argv[1:-1]

  files, stderr = tar_list(tar_file)
  if files is None:
    error("Could not parse tar file listing for '%s':\n%s" % (tar_file, stderr))
    return 1

  if len(base_directories(files)) > 1:
    base = archive_name(tar_file)
    try:
      os.mkdir(base)
    except OSError, e:
      error("Could not create directory '%s': %s" % (base, e))
      return 1
  else:
    base = None
  return untar(tar_file, extra_args=flags, directory=base)

sys.exit(main(sys.argv))

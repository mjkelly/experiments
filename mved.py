#!/usr/bin/python
# -----------------------------------------------------------------
# vimv.py -- Renames files in the current directory through a text editor.
# Copyright 2007 Michael Kelly (michael@michaelkelly.org)
#
# This program is released under the terms of the GNU General Public
# License as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# Sun Feb  7 13:38:06 EST 2010
# -----------------------------------------------------------------

import sys
import os
import re
import tempfile
from optparse import OptionParser, OptionGroup

def sorted_file_list(directory, all=False):
  '''Get a sorted list of the files in the given directory.

  Args:
    all: if true, include hidden (dot) files.
  '''
  hidden = re.compile(r'^\.')
  files = os.listdir(directory)

  hidden = re.compile(r'^\.')
  if not all:
    new_files = []
    for file in files:
      if not hidden.match(file):
        new_files.append(file)
    files = new_files
  
  files.sort()
  return files

def get_editor():
  '''Try to get the user's editor from $EDITOR and $VISUAL. If those
  aren't set, fall back on 'vi'.'''
  editor = os.getenv('EDITOR')
  if editor is None:
    editor = os.getenv('VISUAL')
  if editor is None:
    editor = 'vi'
  return editor

def confirm(msg, default=False):
  '''Prompt the user with message to which they can reply 'y' or 'n'.'''

  if default:
    yesno = " [Y/n] "
  else:
    yesno = " [y/N] "

  sys.stdout.write(msg + yesno)
  response = sys.stdin.readline().strip().lower()

  if default:
    return response != 'n' and response != 'no'
  else:
    return response == 'y' or response == 'yes'

def main(argv):

  opt_parser = OptionParser(usage="%prog [OPTIONS] [PATTERN]")
  opt_parser.add_option("-a", action="store_true", dest="list_all",
    help='List all files (including dotfiles; excluding "." and "..").')
  opt_parser.set_defaults(list_all=False)

  (opts, args) = opt_parser.parse_args()

  cwd = os.getcwd()

  files = sorted_file_list(cwd, opts.list_all)

  editor = get_editor()
  
  (tmpfd, tmpname) = tempfile.mkstemp()
  for file in files:
    os.write(tmpfd, file + "\n")
  os.close(tmpfd)

  pid = os.fork()
  if pid == 0:
    # child
    try:
      os.execvp(editor, [editor, tmpname])
    except RuntimeError, e:
      print e
      sys.exit(1)

  # parent (child ends with execvp)
  (w_pid, w_status) = os.waitpid(pid, 0)

  if w_status != 0:
    print "**** Editor exited with nonzero status (%d)." % w_status
  
  tmp = open(tmpname, 'r')
  i = 0
  new_files = tmp.readlines()
  changes = 0
  for new_file in new_files:
    old_file = files[i]
    new_file = new_file.rstrip('\n\r')
    if files[i] != new_file:
      if new_file != '':
        print "RENAME: '%s' --> '%s'" % (old_file, new_file)
        changes += 1
      else:
        print "DELETE: '%s'" % old_file
        changes += 1
    i += 1
  tmp.close()

  os.unlink(tmpname)

  if len(new_files) != len(files):
    print "ERROR: You added or deleted a line. Don't do that. Use blank lines to delete files."
    sys.exit(1)

  response = False
  if changes > 0:
    response = confirm("Confirm changes?", default=(w_status == 0))

  if response:
    print "Yes. Renaming..."
  else:
    print "No. Aborting."
    sys.exit(0)
  
  i = 0
  while i < len(new_files):
    old_file = files[i]
    new_file = new_files[i].rstrip('\n\r')
    if old_file != new_file:
      try:
        if new_file != '':
          print "RENAME: '%s' --> '%s'" % (old_file, new_file)
          os.rename(old_file, new_file)
        else:
          print "DELETE: '%s'" % old_file
          os.unlink(old_file)
      except OSError, e:
        print e
    i += 1
  
  print "Done."


if __name__ == '__main__':
  main(sys.argv)

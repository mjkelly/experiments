#!/usr/bin/python
# -----------------------------------------------------------------
# mved.py -- Renames files in the current directory through a text editor.
# Copyright 2007 Michael Kelly (michael@michaelkelly.org)
#
# This program is released under the terms of the GNU General Public
# License as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# Sun Feb  7 13:38:06 EST 2010
# Updated Sun Jul  8 03:11:00 EDT 2018
# -----------------------------------------------------------------

import sys
import os
import tempfile
import optparse

def sorted_file_list(directory, all=False):
  '''Get a sorted list of the files in the given directory.

  Args:
    all: if true, include hidden (dot) files.
  '''
  files = os.listdir(directory)

  if not all:
    files = [f for f in files if not f.startswith('.')]
  
  files.sort()
  return files

def get_editor():
  '''Try to get the user's editor from $EDITOR and $VISUAL.
  
  If those aren't set, fall back on 'vi'.
  '''
  return os.getenv('EDITOR', os.getenv('VISUAL', 'vi'))

def confirm(msg, default=False):
  '''Prompt the user with message to which they can reply 'y' or 'n'.'''
  sys.stdout.write(msg + ' [y/N] ')
  sys.stdout.flush()
  response = sys.stdin.readline().strip().lower()
  return response == 'y' or response == 'yes'

def main(argv):
  parser = optparse.OptionParser()
  parser.add_option("-a", action="store_true", dest="list_all",
    help='List all files (including dotfiles; excluding "." and "..").')
  parser.set_defaults(list_all=False)

  opts, args = parser.parse_args()

  cwd = os.getcwd()

  files = sorted_file_list(cwd, opts.list_all)
  editor = get_editor()
  
  tmpfd, tmpname = tempfile.mkstemp()
  for f in files:
    os.write(tmpfd, f + "\n")
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
  w_pid, w_status = os.waitpid(pid, 0)

  if w_status != 0:
    print "%s exited with nonzero status (%d). Aborting." % (editor, w_status)
    sys.exit(2)
  
  tmp = open(tmpname, 'r')
  new_files = tmp.readlines()
  if len(new_files) != len(files):
    print ("ERROR: You added or deleted a line. Don't do that. Use blank "
           "lines to delete files.")
    sys.exit(2)

  new_files = [f.rstrip('\n\r') for f in new_files]

  renames, deletes = 0, 0
  for i, new_file in enumerate(new_files):
    old_file = files[i]
    if files[i] != new_file:
      if new_file != '':
        print "RENAME: '%s' --> '%s'" % (old_file, new_file)
        renames += 1
      else:
        print "DELETE: '%s'" % old_file
        deletes += 1
  tmp.close()

  os.unlink(tmpname)

  response = False
  if renames + deletes > 0:
    response = confirm(
      "Rename %d files and delete %d files?" % (renames, deletes),
      default=False)
  else:
    print "No changes."
    sys.exit(0)

  if not response:
    print "No. Aborting."
    sys.exit(1)
  
  for i, new_file in enumerate(new_files):
    old_file = files[i]
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
  
  print "Done."

if __name__ == '__main__':
  main(sys.argv)

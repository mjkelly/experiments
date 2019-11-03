#!/usr/bin/env python3
# -----------------------------------------------------------------
# mved.py -- Renames files in the current directory through a text editor.
# Copyright 2007 Michael Kelly (michael@michaelkelly.org)
#
# This program is released under the terms of the GNU General Public
# License as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# Sun Feb  7 13:38:06 EST 2010
# Updated Sat Nov  2 22:00:17 EDT 2019
# -----------------------------------------------------------------

import sys
import os
import tempfile
import argparse


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
    '''Try to determine the user's preferred editor'''
    return os.getenv('EDITOR', os.getenv('VISUAL', 'vi'))


def update_files(old_files, new_files, dry_run=True):
    renames, deletes = 0, 0
    for i, new_file in enumerate(new_files):
        old_file = old_files[i]
        if old_files[i] != new_file:
            if new_file != '':
                renames += 1
                if dry_run:
                    print('  mv %s %s' % (old_file, new_file))
                else:
                    os.rename(old_file, new_file)
            else:
                deletes += 1
                if dry_run:
                    print('  rm %s' % old_file)
                else:
                    os.unlink(old_file)
    return renames, deletes


def confirm(msg, default=False):
    '''Prompt the user with message to which they can reply 'y' or 'n'.'''
    sys.stdout.write(msg + ' [y/N] ')
    sys.stdout.flush()
    response = sys.stdin.readline().strip().lower()
    return response == 'y' or response == 'yes'


def main(argv):
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '-a',
        default=False,
        action='store_true',
        dest='list_all',
        help='List all files (including dotfiles; excluding "." and "..").')
    args = parser.parse_args()

    cwd = os.getcwd()
    files = sorted_file_list(cwd, args.list_all)
    editor = get_editor()

    tmpfd, tmpname = tempfile.mkstemp()
    for f in files:
        os.write(tmpfd, bytes(f + '\n', encoding='utf-8'))
    os.close(tmpfd)

    pid = os.fork()
    if pid == 0:
        # child
        try:
            os.execvp(editor, [editor, tmpname])
        except RuntimeError as e:
            print(e)
            sys.exit(1)
    # parent (child ends with execvp)
    w_pid, w_status = os.waitpid(pid, 0)
    if w_status != 0:
        print('%s exited with nonzero status (%d). Aborting.' % (editor,
                                                                 w_status))
        sys.exit(2)

    with open(tmpname, 'r') as tmp:
        new_files = tmp.readlines()
        if len(new_files) != len(files):
            print(
                "ERROR: You added or deleted a line. Don't do that. Use blank "
                'lines to delete files.')
            sys.exit(2)
    os.unlink(tmpname)
    new_files = [f.rstrip('\n\r') for f in new_files]

    renames, deletes = update_files(files, new_files, dry_run=True)
    if renames + deletes == 0:
        print('No changes.')
        sys.exit(0)
    proceed = confirm(
        'Will rename %d and delete %d files. Proceed? ' % (renames, deletes),
        default=False)
    if not proceed:
        print('No. Aborting.')
        sys.exit(1)
    renames, deletes = update_files(files, new_files, dry_run=False)
    print('Renamed %d and deleted %d files.' % (renames, deletes))


if __name__ == '__main__':
    main(sys.argv)

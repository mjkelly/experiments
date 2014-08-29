#!/usr/bin/python

# This script manages a subprocess and provides mechanisms for synchronization
# and setting timeouts. It is designed to make it easier to manage cron jobs
# which may hang, or take unexpectedly long.
#
# Specifically, it provides machanisms to do the following:
# - run a subprocess
# - if that subprocess takes too long to exit, kill it
# - if that subprocess is already running (via this wrapper), abort.
#
# Example usage:
# Run "long_proc -x -y" with a 5s timeout, allowing multiple simultaneous invocations:
#   $ synchro.py --timeout=5 -- long_proc -x -y
# Run long_proc with a 5s timeout; wait for current invocations to finish
# before running:
#   $ synchro.py --synchronous_name longproc --timeout=5 -- long_proc -x -y
# Run long_proc with a 5s timeout; if one is currently running, exit successfully:
#   $ synchro.py --synchronous_name longproc --nonblocking --timeout=5 -- long_proc -x -y

import argparse
import fcntl
import os
import subprocess
import sys
import threading


parser = argparse.ArgumentParser(
        description='Run a subprocess with timeouts and synchronization.')
parser.add_argument('--synchronous_name', '-n', default=None, 
        help='Unique name, for synchronization. We will not start the '
        'subprocess if another synchro script is still running with this '
        'name.')
parser.add_argument('--timeout', '-t', type=float, default=None,
        help='timeout, in seconds. If subprocess takes longer than this, '
        'we send it a SIGTERM, then a SIGKILL (signal 9).')
parser.add_argument('--nonblocking', default=False, action='store_true',
        help='If --synchronous_name is specified, and another process '
        'holds the file lock, exit successfully instead of waiting for lock.')
parser.add_argument('--synchronization_dir',
        default=os.getenv('HOME') + '/.cache/synchro.py',
        help='Where to put synchronization files when using '
        '--synchronous_name')
parser.add_argument('--verbose', '-v', default=False, action='store_true',
        help='Print verbose log messages to stderr.')
parser.add_argument('--kill_timeout', type=float, default=1.0,
        help='How long to wait after SIGTERM before sending SIGKILL.')
parser.add_argument('subprocess',
        help='Name of subprocess to be executed.')
parser.add_argument('subprocess_args', nargs='*', default=[],
        help='Any arguments to subprocess to be executed. Note that you may '
        'need to use "--" before any flags.')


class ProcessThread(threading.Thread):
    """ProcessThread manages subprocess invocation.

    When the subprocess ends, the thread exits. The thread provides mechanisms
    to forcefully kill the subprocess.
    """
    def __init__(self, argv):
        super(ProcessThread, self).__init__()
        self.argv = argv
        self.popen = None

    def run(self):
        try:
            self.popen = subprocess.Popen(self.argv)
            self.popen.wait()
        except OSError as e:
            print >>sys.stderr, e

    def terminate(self):
        if self.popen is not None:
            log('Sending SIGTERM to child process %d' % self.popen.pid)
            self.popen.terminate()

    def kill(self):
        if self.popen is not None:
            log('Sending SIGKILL to child process %d' % self.popen.pid)
            self.popen.kill()


def log(message):
    """Logs a message to stderr if -v was specified."""
    if args.verbose:
        print >>sys.stderr, message


def get_lock():
    """Gets a file lock, if necessary, and using params determined by flags.

    If we cannot obtain the lock, exit. (Either successfully or unsuccessfully,
    depending on flags.)
    """
    fh = None
    # We don't do anything unless --synchronous_name is set.
    if args.synchronous_name is not None:
        if not os.path.isdir(args.synchronization_dir):
            log('--synchronization_dir does not exist, attempting to create')
            os.mkdir(args.synchronization_dir)

        lock = os.path.join(args.synchronization_dir, args.synchronous_name)
        fh = open(lock, 'w')
        log('Acquiring lock on %s' % lock)
        if args.nonblocking:
            try:
                fcntl.flock(fh, fcntl.LOCK_EX | fcntl.LOCK_NB)
            except IOError:
                log('We did not get the lock but --nonblocking is true; '
                        'exiting successfully')
                fh.close()
                sys.exit(0)
        else:
            # Wait indefinitely. Hopefully there is a timeout on the synchro.py
            # holding the lock.
            fcntl.flock(fh, fcntl.LOCK_EX)
        log('Lock acquired')
    return fh


def main():
    fh = get_lock()

    t = ProcessThread([args.subprocess] + args.subprocess_args)
    log('starting subprocess: subprocess=%s, args=%s' % (
        args.subprocess, args.subprocess_args))
    t.start()

    t.join(args.timeout)
    if t.isAlive():
        # If the thread is still alive, we timed out.
        t.terminate()
        t.join(args.kill_timeout)
        if t.isAlive():
            t.kill()

    # The thread has already terminated, or we have forced its subprocess to
    # end, so it is safe to join() with no timeout here.
    t.join()

    if fh is not None:
        fh.close()

    if t.popen is not None:
        log('pid = %d, ret= %d' % (t.popen.pid, t.popen.returncode))
        if t.popen.returncode != 0:
            return 4
    else:
        return 3


args = parser.parse_args()
main()

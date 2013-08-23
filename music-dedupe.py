#!/usr/bin/python
# -----------------------------------------------------------------
# music-dedupe.py -- De-duplicate a directory of music files.
#
# Why music files, specifically? Because we can make lots of assumptions, like:
# 1. Case does not matter.
# 2. Most non-alphanumeric characters don't matter.
#
# Examples:
# "ohGr" vs "OhGr"
# "Burn the Earth, Leave it Behind" vs "Burn the Earth_ Leave it Behin"
# "02 - From Scythe To Sceptre.mp3" vs "02 From Scythe To Sceptre.mp3"
#
# I am specifically targetting differences caused by different cloud music
# services' ideas of what constitutes a "special" character that must be
# escaped.
# Copyright 2013 Michael Kelly (michael@michaelkelly.org)
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
# Thu Aug 22 23:04:50 EDT 2013
# -----------------------------------------------------------------

import os
import re
import sys
import hashlib
import collections

HASH = False


File = collections.namedtuple('File', ['path', 'summarized'])

NON_ALPHA_RE = re.compile(r'\W')

all_files = {}

def summarize(filename):
  """Returns s stripped-down version of the given filename.

  This is to attempt to correct for any over-aggressive escaping.

  Args:
    filename: (str)
  """
  # ' ' -> '%20' is truly fucked up, but it happens.
  new_filename = filename.replace('%20', ' ')
  new_filename = new_filename.lower()
  new_filename = re.sub(NON_ALPHA_RE, '', new_filename)
  return new_filename

for root, dirs, files in os.walk(sys.argv[1]):
  # print 'root=%s, dirs=%s, files=%s' % (root, dirs, files)
  for f in sorted(files + dirs):
    path = os.path.join(root, f)
    # print path

    if HASH:
      with open(path, 'r') as fh:
        print hashlib.md5(fh.read()).hexdigest()

    summarized_path = os.path.join(root, summarize(f))
    if summarized_path in all_files:
      print "dup? %s\n  Already: %s\n  But found: %s" % (summarized_path, all_files[summarized_path].path, path)
    else:
      all_files[summarized_path] = File(path, summarized_path)


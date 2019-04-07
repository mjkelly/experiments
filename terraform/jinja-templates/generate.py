#!/usr/bin/python
'''Generates terraform files from jina2 templates.
'''

import json
import os
import subprocess
import sys

import jinja2

prog = os.path.basename(sys.argv[0])
env = jinja2.Environment(loader=jinja2.FileSystemLoader('.'))
env.filters['json'] = json.dumps

if len(sys.argv) < 2:
    print >> sys.stderr, 'Usage: %s [files]' % prog
    sys.exit(2)

SUFFIX = '.tf.j2'
outfiles = []
for f in sys.argv[1:]:
    if not f.endswith(SUFFIX):
        print 'Skipping %r because filename does not end with %r' % (f, SUFFIX)
        continue
    # Template file at ./app/templates/example.json
    template = env.get_template(f)

    out_f = f.replace(SUFFIX, '.tf')
    outfiles.append(out_f)

    with open(out_f, 'w') as fh:
        print 'Writing %s' % out_f
        fh.write('// Automatically generated from %s by %s\n\n' % (f, prog))
        fh.write(template.render(page={}))

if len(outfiles) > 0:
    print 'Formatting:'
    subprocess.check_call(['terraform', 'fmt'] + outfiles)

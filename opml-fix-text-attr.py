#!/usr/bin/env python
# opml-fix-text-attr.py
# Michael Kelly (michael@michaelkelly.org)
# Thu Mar 14 21:24:35 EDT 2013
# 
# Fixes some broken OPML files by copying the "title" attribute into the "text"
# attribute, if the (required) "text" attribute is missing. Specifically, this
# fixes NetVibes OPML exports.

from xml.dom import minidom
import os
import sys

if len(sys.argv) < 2:
  print("Usage: %s <file>" % sys.argv[0], file=sys.stderr)
  sys.exit(2)

mydom = minidom.parse(sys.argv[1])

unfixable = 0

for outline in mydom.getElementsByTagName('outline'):
  if not outline.getAttribute('text'):
    print("%s is missing text attribute" % outline, file=sys.stderr)

    fixed = False
    alternate_tags = ['title', 'htmlUrl', 'xmlUrl']
    for tag in alternate_tags:
      tag_value = outline.getAttribute(tag)
      if tag_value:
        outline.setAttribute('text', tag_value)
        print("  Using %s attribute (%s)." % (tag, tag_value), file=sys.stderr)
        fixed = True
        break

    if not fixed:
      print("  ! No title attribute.", file=sys.stderr)
      unfixable += 1

if unfixable:
  print("! There were some <outline> elements that could not "
        "be fixed.", file=sys.stderr)
  sys.exit(1)

sys.stdout.buffer.write(mydom.toxml('utf-8'))

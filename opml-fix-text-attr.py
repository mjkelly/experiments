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
  print >>sys.stderr, "Usage: %s <file>" % sys.argv[0]
  sys.exit(2)

mydom = minidom.parse(sys.argv[1])

unfixable = 0

for outline in mydom.getElementsByTagName('outline'):
  if not outline.getAttribute('text'):
    print >>sys.stderr, "%s is missing text attribute" % outline

    fixed = False
    alternate_tags = ['title', 'htmlUrl', 'xmlUrl']
    for tag in alternate_tags:
      tag_value = outline.getAttribute(tag)
      if tag_value:
        outline.setAttribute('text', tag_value)
        print >>sys.stderr, "  Using %s attribute (%s)." % (tag, tag_value)
        fixed = True
        break

    if not fixed:
      print >>sys.stderr, "  ! No title attribute."
      unfixable += 1

if unfixable:
  print >>sys.stderr, ("! There were some <outline> elements that could not "
                       "be fixed.")
  sys.exit(1)

print mydom.toxml('utf-8')

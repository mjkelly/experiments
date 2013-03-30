#!/usr/bin/env python3
#
# This program generates random phrases using words from the system dictionary.
# In the interest of typeability, we only pick words over 3 characters in
# length, which contain no non-ascii characters, and don't end in "'s".
#
# Based on the dictionary size, and other parameters, the program prints some
# quick estimations of the entropy of the resulting phrase(s).
#
# (And Python 3, yarr!)
#
# Michael Kelly
# Fri Mar 29 20:33:53 EDT 2013

import math
import random
import sys

num_words = 4
num_sentences = 10
dictionary = '/usr/share/dict/words'

if len(sys.argv) > 1:
  num_words = int(sys.argv[1])
if len(sys.argv) > 2:
  num_sentences = int(sys.argv[2])

total_word_count = 0
words = []
with open(dictionary, 'r') as fh:
  for line in fh.readlines():
    total_word_count += 1
    line = line.strip()
    if len(line) > 3 and not line.endswith("'s"):
      try:
        line.encode('ascii')
      except UnicodeEncodeError:
        continue
      words.append(line)

# random.sample() chooses a random but unique set of words from the candidates,
# so each word pick is not independent from the others. Because words can't
# repeat, each additional word in the phrase adds a decreasing amount of
# entropy. (The different is miniscule, but nonzero.)
bits_for_first_word = math.log(len(words), 2)
bits_for_last_word = math.log(len(words) - (num_words - 1), 2)
bits_per_phrase = sum([math.log(len(words) - n, 2) for n in range(num_words)])

# To conservatively estimate the reduction in entropy from letting the user
# pick a memorable phrase, we assume an attacker can determine which one was
# picked.
bits_per_pick = bits_per_phrase - math.log(num_sentences, 2)
print("%d possible words (of %d in %s)." % (len(words), total_word_count, dictionary),
      file=sys.stderr)
print("%d words per phrase (random but unique)." % num_words, file=sys.stderr)
print("∴ %f bits of entropy for first word." % bits_for_first_word,
      file=sys.stderr)
print("∴ %f bits of entropy for last word." % bits_for_last_word,
      file=sys.stderr)
print("∴ %f bits of entropy per phrase." % bits_per_phrase, file=sys.stderr)
print("%d phrases to choose from." % num_sentences, file=sys.stderr)
print("∴ %f bits if you pick one phrase from this list." % bits_per_pick,
      file=sys.stderr)
print("---------------------------------------------------", file=sys.stderr)

r = random.SystemRandom()
for _ in range(num_sentences):
  print(*r.sample(words, num_words))

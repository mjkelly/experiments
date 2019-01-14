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
# Sun Jan 13 21:08:54 EST 2019

import math
import random
import sys
import argparse

parser = argparse.ArgumentParser(description='Generate random phrases.')
parser.add_argument(
    'words',
    type=int,
    nargs='?',
    default=5,
    help='How many words per sentence.')
parser.add_argument(
    '--sentences',
    type=int,
    default=10,
    help='How many sentences to print at once.')
parser.add_argument(
    '--simple',
    default=False,
    action='store_true',
    help='Simple mode: Use only lowercase words, without aprostrophes.')
parser.add_argument(
    '--dictionary',
    default='/usr/share/dict/words',
    help='Dictionary file to use. We process the words in this list '
    'somewhat, so we may not end up using all the words. Check the output '
    'of the program.')
args = parser.parse_args()


def bits2length(bits):
    """Estimates the length of a password that has 'bits' entropy."""
    chars = 89  # based on our friend, random-string.py
    return round(bits / math.log(chars, 2))


num_words = args.words
num_sentences = args.sentences

total_word_count = 0
words = []
with open(args.dictionary, 'r') as fh:
    for line in fh.readlines():
        total_word_count += 1
        line = line.strip()
        if len(line) > 2:
            if args.simple:
                if line.lower() != line:
                    continue
                if "'" in line:
                    continue
            try:
                line.encode('ascii')
            except UnicodeEncodeError:
                continue
            words.append(line)

# random.sample() chooses a random but unique set of words from the candidates,
# so each word pick is not independent from the others. Because words can't
# repeat, each additional word in the phrase adds a decreasing amount of
# entropy. (The different is minuscule, but nonzero.)
bits_for_first_word = math.log(len(words), 2)
bits_for_last_word = math.log(len(words) - (num_words - 1), 2)
bits_per_phrase = sum([math.log(len(words) - n, 2) for n in range(num_words)])

# To conservatively estimate the reduction in entropy from letting the user
# pick a memorable phrase, we assume an attacker can determine which one was
# picked.
bits_per_pick = bits_per_phrase - math.log(num_sentences, 2)

corresponding_pw = bits2length(bits_per_phrase)
print(
    "%d possible words (of %d in %s)." % (len(words), total_word_count,
                                          args.dictionary),
    file=sys.stderr)
print("%d words per phrase (random but unique)." % num_words, file=sys.stderr)
print(
    "∴ %f bits of entropy for first word." % bits_for_first_word,
    file=sys.stderr)
print(
    "∴ %f bits of entropy for last word." % bits_for_last_word,
    file=sys.stderr)
print("∴ %f bits of entropy per phrase." % bits_per_phrase, file=sys.stderr)
print(
    "(approximately equivalent to %d char random password)" % corresponding_pw,
    file=sys.stderr)
print("%d phrases to choose from." % num_sentences, file=sys.stderr)
print(
    "∴ %f bits if you pick one phrase from this list." % bits_per_pick,
    file=sys.stderr)
print("---------------------------------------------------", file=sys.stderr)

r = random.SystemRandom()
for _ in range(num_sentences):
    print(*r.sample(words, num_words))

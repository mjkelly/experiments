#!/usr/bin/python

import sys

COLORS = [1, 2, 3, 4, 5, 6]

color_map = {
    'picked': {},
    'next': 0,
}


def pick_color(container_id):
    if container_id not in color_map['picked']:
        color_map['picked'][container_id] = color_map['next']
        color_map['next'] = (color_map['next'] + 1) % len(COLORS)
    return color_map['picked'][container_id]


def colorize(msg, color):
    code = 30 + color
    return f'\N{ESC}[{code}m{msg}\u001b[0m'


while True:
    line = sys.stdin.readline()
    if len(line) == 0:
        break
    container_id, rest = line.split(" ", 1)
    container_str = colorize(container_id, COLORS[pick_color(container_id)])
    print(f"{container_str} {rest}", end='')

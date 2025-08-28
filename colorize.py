#!/usr/bin/python

import argparse
import sys

COLORS = [1, 2, 3, 4, 5, 6]

color_map = {
    'picked': {},
    'next': 0,
}


def pick_color(container_id: str) -> int:
    if container_id not in color_map['picked']:
        color_map['picked'][container_id] = color_map['next']
        color_map['next'] = (color_map['next'] + 1) % len(COLORS)
    return color_map['picked'][container_id]


def colorize(msg: str, color: int) -> str:
    code = 30 + color
    return f'\N{ESC}[{code}m{msg}\u001b[0m'


def colorize_line(line: str, field: int, sep: str) -> str:
    parts = line.split(sep)
    color = COLORS[pick_color(parts[field])]
    parts[field] = colorize(parts[field], color)
    return sep.join(parts)


def parse_args():
    parser = argparse.ArgumentParser(
        description='Add deterministic color to logs')
    parser.add_argument('--field',
                        default=0,
                        type=int,
                        help='Field to colorize')
    parser.add_argument('--sep',
                        default=" ",
                        type=str,
                        help='Separator between fields')
    return parser.parse_args()


def main():
    args = parse_args()
    while True:
        line = sys.stdin.readline()
        if len(line) == 0:
            break
        print(colorize_line(line, args.field, args.sep), end='')
        # container_id, rest = line.split(" ", 1)
        # container_str = colorize(container_id,
        #                          COLORS[pick_color(container_id)])
        # print(f"{container_str} {rest}", end='')


if __name__ == '__main__':
    main()

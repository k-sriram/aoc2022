from __future__ import annotations

import argparse
import os.path

import pytest
from termcolor import colored

import support

os.system("color")

INPUT_TXT = os.path.join(os.path.dirname(__file__), "input.txt")

SHAPES = [
    (
        [(0, 0), (0, 1), (0, 2), (0, 3)],
        (
            [(0, 4)],
            [(0, -1)],
            [(-1, 0), (-1, 1), (-1, 2), (-1, 3)],
        ),
        "-",
    ),
    (
        [(0, 1), (1, 0), (1, 1), (1, 2), (2, 1)],
        (
            [(0, 2), (1, 3), (2, 2)],
            [(0, 0), (1, -1), (2, 0)],
            [(0, 0), (-1, 1), (0, 2)],
        ),
        "+",
    ),
    (
        [(0, 0), (0, 1), (0, 2), (1, 2), (2, 2)],
        (
            [(0, 3), (1, 3), (2, 3)],
            [(0, -1), (1, 1), (2, 1)],
            [(-1, 0), (-1, 1), (-1, 2)],
        ),
        "L",
    ),
    (
        [(0, 0), (1, 0), (2, 0), (3, 0)],
        (
            [(0, 1), (1, 1), (2, 1), (3, 1)],
            [(0, -1), (1, -1), (2, -1), (3, -1)],
            [(-1, 0)],
        ),
        "|",
    ),
    (
        [(0, 0), (0, 1), (1, 0), (1, 1)],
        (
            [(0, 2), (1, 2)],
            [(0, -1), (1, -1)],
            [(-1, 0), (-1, 1)],
        ),
        "o",
    ),
]

COLORS = ["red", "green", "yellow", "blue", "magenta", "cyan", "white"]


def generate_rock(
    round: int, height: int
) -> tuple[list[int], list[tuple[int, int]], tuple[list[tuple[int, int]], ...], str]:
    pos = [height + 3, 2]
    return pos, *SHAPES[round % len(SHAPES)]


def moveblock(
    chamber: list[list[str]],
    pos: list[int],
    blocks: tuple[list[tuple[int, int]], ...],
    direction: str,
) -> bool:
    sideblock = blocks[{">": 0, "<": 1}[direction]]
    downblock = blocks[2]
    if all(
        pos[1] + dx >= 0
        and pos[1] + dx < 7
        and chamber[pos[0] + dy][pos[1] + dx] == "."
        for dy, dx in sideblock
    ):
        # print(f"Moving {direction} from {pos} to ", end="")
        pos[1] += {">": 1, "<": -1}[direction]
        # print(pos)

    if all(
        pos[1] + dx >= 0
        and pos[1] + dx < 7
        and pos[0] + dy >= 0
        and chamber[pos[0] + dy][pos[1] + dx] == "."
        for dy, dx in downblock
    ):
        # print(f"Moving v from {pos} to ", end="")
        pos[0] -= 1
        # print(pos)
        return True

    return False


def compute(s: str) -> int:
    s = s.strip()
    heights = []
    chamber = [["." for _ in range(7)] for _ in range(1000000)]
    n = len(s)
    i = 0
    height = 0
    # for round in range(58465):
    for round in range(1440):
        pos, shape, blocks, glyph = generate_rock(round, height)
        # print(pos)
        while moveblock(chamber, pos, blocks, s[i % n]):
            i += 1

        for p, (x, y) in enumerate(shape):
            try:
                if glyph == "-":
                    glyphp = round % (10 ** (4 - p)) // (10 ** (3 - p))
                else:
                    glyphp = glyph
                chamber[pos[0] + x][pos[1] + y] = colored(
                    glyphp, COLORS[(i % len(s)) % len(COLORS)]
                )
            except IndexError:
                print(pos, x, y, i, round)
                raise
            height = max(height, pos[0] + x + 1)

        i += 1
        # print("Round", round, "height", height, "i", i)
        heights.append(height)

    print(heights)
    rows = []
    for h in range(height, -1, -1):
        rows.append("".join(chamber[h]))
    splitn = 17
    split = len(rows) // splitn
    rem = len(rows) % splitn
    if rem:
        rows = ["......."] * (splitn - rem) + rows
        split += 1
    for i in range(split):
        print(f"{(100-i)%100:2d}", end=" ")
        if i % 100 == 0:
            for j in range(splitn):
                print(f"{split - i + split * (splitn - j - 1):>7d}", end="  ")
            print()
            print(f"{(100-i)%100:2d}", end=" ")
        for j in range(splitn):
            print(rows[i + split * j], end="  ")
        print()
    print(f"{split=}")
    return height


INPUT_S = """\
>>><<><>><<<>><>>><<<>>><<<><<<>><>><<>>
"""
EXPECTED = 1514285714288


@pytest.mark.parametrize(
    ("input_s", "expected"),
    ((INPUT_S, EXPECTED),),
)
def test(input_s: str, expected: int) -> None:
    assert compute(input_s) == expected


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("data_file", nargs="?", default=INPUT_TXT)
    args = parser.parse_args()

    with open(args.data_file) as f, support.timing():  # type: ignore[attr-defined]
        print(compute(f.read()))

    return 0


if __name__ == "__main__":
    raise SystemExit(main())

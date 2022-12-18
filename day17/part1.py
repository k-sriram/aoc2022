from __future__ import annotations

import argparse
import os.path
import sys

import pytest

import support

Blocks = list[tuple[int, int]]
BlockSet = tuple[Blocks, Blocks, Blocks]


INPUT_TXT = os.path.join(os.path.dirname(__file__), "input.txt")

SHAPES = [
    (
        [(0, 0), (0, 1), (0, 2), (0, 3)],
        (
            [(0, 4)],
            [(0, -1)],
            [(-1, 0), (-1, 1), (-1, 2), (-1, 3)],
        ),
    ),
    (
        [(0, 1), (1, 0), (1, 1), (1, 2), (2, 1)],
        (
            [(0, 2), (1, 3), (2, 2)],
            [(0, 0), (1, -1), (2, 0)],
            [(0, 0), (-1, 1), (0, 2)],
        ),
    ),
    (
        [(0, 0), (0, 1), (0, 2), (1, 2), (2, 2)],
        (
            [(0, 3), (1, 3), (2, 3)],
            [(0, -1), (1, 1), (2, 1)],
            [(-1, 0), (-1, 1), (-1, 2)],
        ),
    ),
    (
        [(0, 0), (1, 0), (2, 0), (3, 0)],
        (
            [(0, 1), (1, 1), (2, 1), (3, 1)],
            [(0, -1), (1, -1), (2, -1), (3, -1)],
            [(-1, 0)],
        ),
    ),
    (
        [(0, 0), (0, 1), (1, 0), (1, 1)],
        (
            [(0, 2), (1, 2)],
            [(0, -1), (1, -1)],
            [(-1, 0), (-1, 1)],
        ),
    ),
]


def generate_rock(
    round: int, height: int
) -> tuple[list[int], list[tuple[int, int]], BlockSet]:
    pos = [height + 3, 2]
    return pos, *SHAPES[round % len(SHAPES)]


def moveblock(
    chamber: list[list[str]], pos: list[int], blocks: BlockSet, direction: str
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
    chamber = [["." for _ in range(7)] for _ in range(1000000)]
    n = len(s)
    i = 0
    height = 0
    for round in range(2022):
        pos, shape, blocks = generate_rock(round, height)
        # print(pos)
        while moveblock(chamber, pos, blocks, s[i % n]):
            i += 1

        for x, y in shape:
            try:
                chamber[pos[0] + x][pos[1] + y] = "#"
            except IndexError:
                print(pos, x, y, i, round, file=sys.stderr)
                raise
            height = max(height, pos[0] + x + 1)

        i += 1
        # print("Round", round, "height", height, "i", i)

    return height


INPUT_S = """\
>>><<><>><<<>><>>><<<>>><<<><<<>><>><<>>
"""
EXPECTED = 3068


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

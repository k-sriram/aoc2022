from __future__ import annotations

import argparse
import os.path
import sys

import pytest

import support

INPUT_TXT = os.path.join(os.path.dirname(__file__), "input.txt")


def compute(s: str) -> int:
    gridsize = 1000
    grid = [[False for i in range(gridsize)] for j in range(gridsize)]
    curhead = (gridsize // 2, gridsize // 2)
    curtail = curhead
    grid[curtail[0]][curtail[1]] = True
    for line in s.splitlines():
        dir_letter, steps = line[0], int(line[2:])
        direction = {"U": (-1, 0), "D": (1, 0), "L": (0, -1), "R": (0, 1)}[dir_letter]

        for _ in range(steps):
            curhead = (curhead[0] + direction[0], curhead[1] + direction[1])
            curtail = movetail(curhead, curtail)
            # print(curhead, curtail, file=sys.stderr)
            grid[curtail[0]][curtail[1]] = True
    # printgrid(grid)
    return sum(sum(row) for row in grid)


def movetail(curhead: tuple[int, int], curtail: tuple[int, int]) -> tuple[int, int]:
    for i in range(-1, 2):
        for j in range(-1, 2):
            if (curhead[0] + i, curhead[1] + j) == curtail:
                return curtail
    return (
        int(curtail[0] + sign(curhead[0] - curtail[0])),
        int(curtail[1] + sign(curhead[1] - curtail[1])),
    )


def sign(x: int) -> int:
    return 1 if x > 0 else -1 if x < 0 else 0


def printgrid(grid: list[list[bool]]) -> None:
    for row in grid:
        for col in row:
            print("#" if col else ".", end="", file=sys.stderr)
        print(file=sys.stderr)


INPUT_S = """R 4
U 4
L 3
D 1
R 4
D 1
L 5
R 2
"""
EXPECTED = 13


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

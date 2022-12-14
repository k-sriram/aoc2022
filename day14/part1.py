from __future__ import annotations

import argparse
import os.path
import sys

import pytest

import support

INPUT_TXT = os.path.join(os.path.dirname(__file__), "input.txt")

MAX_Y = 1000


def compute(s: str) -> int:
    y_bound = 0
    cavemap = [["." for _ in range(1000)] for _ in range(MAX_Y)]
    start = (500, 0)
    for line in s.splitlines():
        points = line.split(" -> ")
        for point in points:
            cur = [int(x) for x in point.split(",")]
            if y_bound <= cur[1]:
                y_bound = cur[1]

        cur = [int(x) for x in points[0].split(",")]
        for point in points[1:]:
            next = [int(x) for x in point.split(",")]
            while cur != next:
                if MAX_Y <= cur[1]:
                    print("Out of bounds", file=sys.stderr)
                    sys.exit(1)
                cavemap[cur[1]][cur[0]] = "#"
                if cur[0] < next[0]:
                    cur[0] += 1
                elif cur[0] > next[0]:
                    cur[0] -= 1
                elif cur[1] < next[1]:
                    cur[1] += 1
                elif cur[1] > next[1]:
                    cur[1] -= 1
            cavemap[cur[1]][cur[0]] = "#"
    cavemap[start[1]][start[0]] = "+"

    # printmap(cavemap, y_bound)

    sands = []
    try:
        while True:
            if cavemap[start[1]][start[0]] == "o":
                break
            cursand = list(start)
            while True:
                if cavemap[cursand[1] + 1][cursand[0]] == ".":
                    cursand[1] += 1
                elif cavemap[cursand[1] + 1][cursand[0] - 1] == ".":
                    cursand[0] -= 1
                    cursand[1] += 1
                elif cavemap[cursand[1] + 1][cursand[0] + 1] == ".":
                    cursand[0] += 1
                    cursand[1] += 1
                else:
                    break
            cavemap[cursand[1]][cursand[0]] = "o"
            sands.append(cursand)
    except IndexError:
        pass
    printmap(cavemap, y_bound)
    return len(sands)


def printmap(cavemap: list[list[str]], y_bound: int) -> None:
    bounds = [500, 500]
    for x in range(500, 1000):
        col = [row[x] for row in cavemap[0 : y_bound + 1]]
        if all(c == "." for c in col):
            bounds[1] = x
            break
    for x in range(500, 0, -1):
        col = [row[x] for row in cavemap[0 : y_bound + 1]]
        if all(c == "." for c in col):
            bounds[0] = x
            break
    for row in cavemap[0 : y_bound + 1]:
        print("".join(row[bounds[0] : bounds[1] + 1]), file=sys.stderr)


INPUT_S = """498,4 -> 498,6 -> 496,6
503,4 -> 502,4 -> 502,9 -> 494,9
"""
EXPECTED = 24


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

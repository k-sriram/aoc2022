from __future__ import annotations

import argparse
import os.path
import re

import pytest

import support

INPUT_TXT = os.path.join(os.path.dirname(__file__), "input.txt")
Y_LEVEL = 2000000


line_re = re.compile(
    r"Sensor at x=(-?\d+), y=(-?\d+): closest beacon is at x=(-?\d+), y=(-?\d+)"
)


def compute(s: str, y: int) -> int:
    blocks = set()
    beacons = set()
    for line in s.splitlines():
        sxstr, systr, bxstr, bystr = line_re.match(
            line
        ).groups()  # type: ignore[union-attr]
        sx, sy, bx, by = map(int, (sxstr, systr, bxstr, bystr))
        if by == y:
            beacons.add(bx)
        distance = abs(sx - bx) + abs(sy - by)
        xrange = distance - abs(sy - y)
        for x in range(sx - xrange, sx + xrange + 1):
            blocks.add((x, y))
    return len(blocks) - len(beacons)


INPUT_S = """\
Sensor at x=2, y=18: closest beacon is at x=-2, y=15
Sensor at x=9, y=16: closest beacon is at x=10, y=16
Sensor at x=13, y=2: closest beacon is at x=15, y=3
Sensor at x=12, y=14: closest beacon is at x=10, y=16
Sensor at x=10, y=20: closest beacon is at x=10, y=16
Sensor at x=14, y=17: closest beacon is at x=10, y=16
Sensor at x=8, y=7: closest beacon is at x=2, y=10
Sensor at x=2, y=0: closest beacon is at x=2, y=10
Sensor at x=0, y=11: closest beacon is at x=2, y=10
Sensor at x=20, y=14: closest beacon is at x=25, y=17
Sensor at x=17, y=20: closest beacon is at x=21, y=22
Sensor at x=16, y=7: closest beacon is at x=15, y=3
Sensor at x=14, y=3: closest beacon is at x=15, y=3
Sensor at x=20, y=1: closest beacon is at x=15, y=3
"""
EXPECTED = 26


@pytest.mark.parametrize(
    ("input_s", "y", "expected"),
    ((INPUT_S, 10, EXPECTED),),
)
def test(input_s: str, y: int, expected: int) -> None:
    assert compute(input_s, y) == expected


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("data_file", nargs="?", default=INPUT_TXT)
    args = parser.parse_args()

    with open(args.data_file) as f, support.timing():  # type: ignore[attr-defined]
        print(compute(f.read(), Y_LEVEL))

    return 0


if __name__ == "__main__":
    raise SystemExit(main())

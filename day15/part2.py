from __future__ import annotations

import argparse
import os.path
import re

import pytest
from tqdm import tqdm

import support

INPUT_TXT = os.path.join(os.path.dirname(__file__), "input.txt")
MAX_COOR = 4_000_000


line_re = re.compile(
    r"Sensor at x=(-?\d+), y=(-?\d+): closest beacon is at x=(-?\d+), y=(-?\d+)"
)


def compute(s: str, max_coor: int) -> int:
    # Parse the input
    sensors = {}
    for line in s.splitlines():
        sxstr, systr, bxstr, bystr = line_re.match(
            line
        ).groups()  # type: ignore[union-attr]
        sx, sy, bx, by = map(int, (sxstr, systr, bxstr, bystr))
        distance = abs(sx - bx) + abs(sy - by)
        sensors[(sx, sy)] = distance

    # If there is only one possible space outside sensor range, it should be
    # be just outside the sensor range. Create a list of all possible spaces.
    # Using a list to store the space since using a set is not performant
    # despite the fact that it would lead to us checking some values multiple
    # times.
    perimeters = []
    for (sx, sy), distance in tqdm(sensors.items()):
        for i in range(distance + 1):
            perimeters.append((sx - distance - 1 + i, sy - i))
            perimeters.append((sx + i, sy - distance - 1 + i))
            perimeters.append((sx + distance + 1 - i, sy + i))
            perimeters.append((sx - i, sy + distance + 1 - i))

    # Check each possible space to see if it is outside the sensor range.
    for (x, y) in tqdm(perimeters):
        if x < 0 or x > max_coor or y < 0 or y > max_coor:
            continue
        for sx, sy in sensors:
            if abs(x - sx) + abs(y - sy) <= sensors[(sx, sy)]:
                break
        else:  # no break
            return tuning_freq(x, y)

    raise ValueError("No solution found")


def tuning_freq(x: int, y: int) -> int:
    return x * 4000000 + y


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
EXPECTED = 56000011


@pytest.mark.parametrize(
    ("input_s", "max_coor", "expected"),
    ((INPUT_S, 20, EXPECTED),),
)
def test(input_s: str, max_coor: int, expected: int) -> None:
    assert compute(input_s, max_coor) == expected


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("data_file", nargs="?", default=INPUT_TXT)
    args = parser.parse_args()

    with open(args.data_file) as f, support.timing():  # type: ignore[attr-defined]
        print(compute(f.read(), MAX_COOR))

    return 0


if __name__ == "__main__":
    raise SystemExit(main())

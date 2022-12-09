from __future__ import annotations

import argparse
import os.path
from typing import Iterable

import pytest

import support

INPUT_TXT = os.path.join(os.path.dirname(__file__), "input.txt")


def compute(s: str) -> int:
    calories: list[list[int]] = [[]]

    lines = s.splitlines()
    for line in lines:
        if line != "":
            calories[-1].append(int(line))
        else:
            calories.append([])

    sums = [sum(ec) for ec in calories]
    return sum(topn(sums, 3))


def topn(L: Iterable[int], n: int) -> list[int]:
    toplist: list[int] = []
    for i in L:
        if len(toplist) < n:
            reverse_insort(toplist, i)
        elif i > toplist[-1]:
            reverse_insort(toplist, i)
            toplist = toplist[:n]
    return toplist


def reverse_insort(a: list[int], x: int, lo: int = 0, hi: int | None = None) -> None:
    """Insert item x in list a, and keep it reverse-sorted assuming a
    is reverse-sorted.

    If x is already in a, insert it to the right of the rightmost x.

    Optional args lo (default 0) and hi (default len(a)) bound the
    slice of a to be searched.
    """
    if lo < 0:
        raise ValueError("lo must be non-negative")
    if hi is None:
        hi = len(a)
    while lo < hi:
        mid = (lo + hi) // 2
        if x > a[mid]:
            hi = mid
        else:
            lo = mid + 1
    a.insert(lo, x)


INPUT_S = """\
1000
2000
3000

4000

5000
6000

7000
8000
9000

10000
"""
EXPECTED = 45000


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

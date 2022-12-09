from __future__ import annotations

import argparse
import os.path
from typing import Iterator
from typing import TypeVar

import pytest

import support

INPUT_TXT = os.path.join(os.path.dirname(__file__), "input.txt")


T = TypeVar("T")


def chunked(it: Iterator[T], n: int) -> Iterator[list[T]]:
    i = 0
    chunk = []
    for item in it:
        chunk.append(item)
        i += 1
        if i % n == 0:
            i = 0
            yield chunk
            chunk = []
    if chunk != []:
        yield chunk


def compute(s: str) -> int:
    priority = 0

    lines = (L for L in s.splitlines() if L)
    for lines3 in chunked(lines, 3):
        intersect = set(lines3.pop())
        for s in lines3:
            intersect = intersect.intersection(s)
        priority += get_priority(intersect.pop())
    return priority


def get_priority(c: str) -> int:
    spam = (ord(c) - 96) % 64
    if spam > 30:
        spam -= 6
    return spam


INPUT_S = """vJrwpWtwJgWrhcsFMMfFFhFp
jqHRNqRjqzjGDLGLrsFMfFZSrLrFZsSL
PmmdzqPrVvPwwTWBwg
wMqvLMZHhHMvwLHjbvcjnnSBnvTQFn
ttgJtRGJQctTZtZT
CrZsJsPPZsGzwwsLwLmpwMDw
"""
EXPECTED = 70


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

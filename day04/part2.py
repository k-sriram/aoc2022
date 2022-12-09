from __future__ import annotations

import argparse
import os.path

import pytest

import support

INPUT_TXT = os.path.join(os.path.dirname(__file__), "input.txt")


def compute(s: str) -> int:
    subgroups = 0

    lines = s.splitlines()
    for line in lines:
        a, b = parse_group(line)
        if a.intersection(b):
            subgroups += 1
    return subgroups


def parse_group(line: str) -> list[set[int]]:
    assignments = line.split(",")
    groups = []
    for ass in assignments:
        edges = [int(x) for x in ass.split("-")]
        groups.append(set(range(edges[0], edges[1] + 1)))
    return groups


INPUT_S = """2-4,6-8
2-3,4-5
5-7,7-9
2-8,3-7
6-6,4-6
2-6,4-8
"""
EXPECTED = 4


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

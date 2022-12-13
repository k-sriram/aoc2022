from __future__ import annotations

import argparse
import os.path
from functools import cmp_to_key

import pytest

import support

INPUT_TXT = os.path.join(os.path.dirname(__file__), "input.txt")

NestedList = int | list["NestedList"]


def compute(s: str) -> int:
    signals = []
    for line in s.splitlines():
        if line:
            signals.append(eval(line))
    signals.extend([[[2]], [[6]]])
    signals.sort(key=cmp_to_key(cmp))
    return (signals.index([[2]]) + 1) * (signals.index([[6]]) + 1)


def cmp(a: NestedList, b: NestedList) -> int:
    if isinstance(a, int) and isinstance(b, int):
        if a == b:
            return 0
        return -1 if a < b else 1
    if isinstance(a, list) and isinstance(b, list):
        for (x, y) in zip(a, b):
            if cmp(x, y) == 0:
                continue
            return cmp(x, y)
        if len(a) == len(b):
            return 0
        return -1 if len(a) < len(b) else 1
    if isinstance(a, list) and isinstance(b, int):
        return cmp(a, [b])
    if isinstance(a, int) and isinstance(b, list):
        return cmp([a], b)
    raise ValueError(f"Unexpected types: {a}, {b}")


INPUT_S = """[1,1,3,1,1]
[1,1,5,1,1]

[[1],[2,3,4]]
[[1],4]

[9]
[[8,7,6]]

[[4,4],4,4]
[[4,4],4,4,4]

[7,7,7,7]
[7,7,7]

[]
[3]

[[[]]]
[[]]

[1,[2,[3,[4,[5,6,7]]]],8,9]
[1,[2,[3,[4,[5,6,0]]]],8,9]
"""
EXPECTED = 140


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

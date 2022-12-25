from __future__ import annotations

import argparse
import os.path

import pytest

import support

INPUT_TXT = os.path.join(os.path.dirname(__file__), "input.txt")

PLACE_VALUE = {
    "=": -2,
    "-": -1,
    "0": 0,
    "1": 1,
    "2": 2,
}

PLACE_SYMBOLS = {v: k for k, v in PLACE_VALUE.items()}


def int_from_snafu(x: str) -> int:
    mul = 1
    res = 0
    for c in reversed(x):
        res += PLACE_VALUE[c] * mul
        mul *= 5
    return res


def snafu_from_int(x: int) -> str:
    pv = []
    while x:
        pv.append(x % 5)
        x //= 5
    for i, v in enumerate(pv):
        if v > 2:
            pv[i] -= 5
            if i + 1 < len(pv):
                pv[i + 1] += 1
            else:
                pv.append(1)
    return "".join(PLACE_SYMBOLS[v] for v in reversed(pv))


def compute(s: str) -> str:
    nums = [int_from_snafu(x) for x in s.splitlines()]
    result_in_decimal = sum(nums)
    return snafu_from_int(result_in_decimal)


INPUT_S = """\
1=-0-2
12111
2=0=
21
2=01
111
20012
112
1=-1=
1-12
12
1=
122
"""
EXPECTED = "2=-1=0"


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

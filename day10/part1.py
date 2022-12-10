from __future__ import annotations

import argparse
import os.path

import pytest

import support

INPUT_TXT = os.path.join(os.path.dirname(__file__), "input.txt")


def compute(s: str) -> int:
    cycle = 1
    x = 1
    counter = 0
    for line in s.splitlines():
        if line == "noop":
            cycle += 1
            if is_record_cycle(cycle):
                counter += x * cycle
        if line.startswith("addx"):
            cycle += 1
            if is_record_cycle(cycle):
                counter += x * cycle
            x += int(line.split()[1])
            cycle += 1
            if is_record_cycle(cycle):
                counter += x * cycle
    return counter


def is_record_cycle(cycle: int) -> bool:
    return cycle % 40 == 20


with open("test_input.txt") as f:
    INPUT_S = f.read()
EXPECTED = 13140


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

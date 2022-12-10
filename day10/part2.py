from __future__ import annotations

import argparse
import os.path
from typing import Any
from typing import Callable
from typing import Iterator

import pytest

import support

INPUT_TXT = os.path.join(os.path.dirname(__file__), "input.txt")


def compute(s: str) -> None:
    reg = init_reg(s)
    screen = [["." for _ in range(40)] for _ in range(6)]
    for i, regx in enumerate(reg()):
        x = i % 40
        y = i // 40
        if abs(regx - x) <= 1:
            screen[y][x] = "#"
    for line in screen:
        print("".join(line))

    return


def init_reg(s: str) -> Callable[[], Iterator[int]]:
    def get_reg() -> Iterator[int]:
        x = 1
        yield x
        for line in s.splitlines():
            if line == "noop":
                yield x
            if line.startswith("addx"):
                yield x
                x += int(line.split()[1])
                yield x

    return get_reg


with open("test_input.txt") as f:
    INPUT_S = f.read()
EXPECTED = """\
##..##..##..##..##..##..##..##..##..##..
###...###...###...###...###...###...###.
####....####....####....####....####....
#####.....#####.....#####.....#####.....
######......######......######......####
#######.......#######.......#######.....
"""


@pytest.mark.parametrize(
    ("input_s", "expected"),
    ((INPUT_S, EXPECTED),),
)
def test(input_s: str, expected: int, capsys: Any) -> None:
    compute(input_s)
    assert capsys.readouterr().out == expected


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("data_file", nargs="?", default=INPUT_TXT)
    args = parser.parse_args()

    with open(args.data_file) as f, support.timing():  # type: ignore[attr-defined]
        compute(f.read())

    return 0


if __name__ == "__main__":
    raise SystemExit(main())

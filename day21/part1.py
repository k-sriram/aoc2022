from __future__ import annotations

import argparse
import os.path
from collections import deque
from dataclasses import dataclass
from typing import Deque

import pytest

import support

INPUT_TXT = os.path.join(os.path.dirname(__file__), "input.txt")


@dataclass
class Operation:
    first: str
    second: str
    op: str


def operate(vars: dict[str, int | Operation], var: str) -> int | None:
    match vars[var]:
        case int(val):
            return val
        case Operation(first, second, op):
            first_val, second_val = vars[first], vars[second]
            match (first_val, second_val):
                case (int(first_val), int(second_val)):
                    if op == "+":
                        return first_val + second_val
                    elif op == "-":
                        return first_val - second_val
                    elif op == "*":
                        return first_val * second_val
                    elif op == "/":
                        return first_val // second_val
                    else:
                        raise ValueError(f"Unknown operation {op}")
                case _:
                    return None
    raise ValueError(f"Unknown type {type(vars[var])}")


def parse_operation(s: str) -> int | Operation:
    try:
        return int(s)
    except ValueError:
        first, op, second = s.split()
        return Operation(first, second, op)


def compute(s: str) -> int:
    triggers: dict[str, list[str]] = {}  # when a variable is updated, trigger these
    # triggers to be processed, these variables are already known to be ints
    trigger_queue: Deque[str] = deque()
    vars: dict[str, int | Operation] = {}
    for line in s.splitlines():
        var, op = line.split(": ")
        val = parse_operation(op)
        vars[var] = val
        if isinstance(val, int):
            trigger_queue.append(var)
        else:
            triggers.setdefault(val.first, []).append(var)
            triggers.setdefault(val.second, []).append(var)

    while trigger_queue:
        var = trigger_queue.popleft()
        for trigger in triggers.get(var, []):
            result = operate(vars, trigger)
            if result is not None:
                vars[trigger] = result
                trigger_queue.append(trigger)

    rootval = vars["root"]
    if isinstance(rootval, Operation):
        raise ValueError("root could not be computed")
    return rootval


INPUT_S = """\
root: pppw + sjmn
dbpl: 5
cczh: sllz + lgvd
zczc: 2
ptdq: humn - dvpt
dvpt: 3
lfqf: 4
humn: 5
ljgn: 2
sjmn: drzm * dbpl
sllz: 4
pppw: cczh / lfqf
lgvd: ljgn * ptdq
drzm: hmdt - zczc
hmdt: 32
"""
EXPECTED = 152


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

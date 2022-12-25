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


class Unknown:
    pass


def operate(vars: dict[str, int | Operation | Unknown], var: str) -> int | None:
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
        case Unknown():
            raise NotImplementedError("Unknown value")
    raise ValueError(f"Unknown type {type(vars[var])}")


def parse_operation(s: str) -> int | Operation:
    try:
        return int(s)
    except ValueError:
        first, op, second = s.split()
        return Operation(first, second, op)


def solve(
    vars: dict[str, int | Operation | Unknown], operation: Operation, target: int
) -> tuple[str, int]:
    firstval, secondval = vars[operation.first], vars[operation.second]
    if isinstance(firstval, int):
        known, unknown, knownvar = firstval, operation.second, 1
    elif isinstance(secondval, int):
        known, unknown, knownvar = secondval, operation.first, 2
    else:
        raise ValueError(f"Both operands are unknown: {operation}")

    if operation.op == "+":
        return unknown, target - known
    elif operation.op == "-":
        if knownvar == 1:
            return unknown, known - target
        else:
            return unknown, known + target
    elif operation.op == "*":
        return unknown, target // known
    elif operation.op == "/":
        if knownvar == 1:
            return unknown, known // target
        else:
            return unknown, known * target
    raise ValueError(f"Unknown operation {operation.op}")


def compute(s: str) -> int:
    triggers: dict[str, list[str]] = {}  # when a variable is updated, trigger these
    # triggers to be processed, these variables are already known to be ints
    trigger_queue: Deque[str] = deque()
    solve_queue: Deque[tuple[str, int]] = deque()
    vars: dict[str, int | Operation | Unknown] = {}
    for line in s.splitlines():
        var, op = line.split(": ")
        val: int | Operation | Unknown = parse_operation(op)
        if var == "humn":
            val = Unknown()
        if var == "root":
            assert isinstance(val, Operation)
            val.op = "="
        vars[var] = val
        if isinstance(val, int):
            trigger_queue.append(var)
        elif isinstance(val, Operation):
            triggers.setdefault(val.first, []).append(var)
            triggers.setdefault(val.second, []).append(var)

    while trigger_queue:
        var = trigger_queue.popleft()
        for trigger in triggers.get(var, []):
            if trigger == "root":
                rootvar = vars["root"]
                assert isinstance(rootvar, Operation)
                firstvar, secondvar = vars[rootvar.first], vars[rootvar.second]
                if isinstance(firstvar, int):
                    solve_queue.append((rootvar.second, firstvar))
                elif isinstance(secondvar, int):
                    solve_queue.append((rootvar.first, secondvar))
                continue
            result = operate(vars, trigger)
            if result is not None:
                vars[trigger] = result
                if trigger not in trigger_queue:
                    trigger_queue.append(trigger)

    while solve_queue:
        var, target = solve_queue.popleft()
        operation = vars[var]
        assert isinstance(operation, Operation)
        targetvar, targetval = solve(vars, operation, target)
        if isinstance(vars[targetvar], int):
            raise ValueError("targetvar is already known")
        elif isinstance(vars[targetvar], Unknown):
            vars[targetvar] = targetval
        else:
            vars[var] = targetval
            solve_queue.append((targetvar, targetval))

    humnval = vars["humn"]
    if not isinstance(humnval, int):
        raise ValueError(f"humn could not be computed, {humnval}")
    return humnval


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
EXPECTED = 301


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

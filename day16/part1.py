from __future__ import annotations

import argparse
import os.path
import re
import sys
from collections import deque

import pytest

import support

INPUT_TXT = os.path.join(os.path.dirname(__file__), "input.txt")

node_re = re.compile(
    r"Valve (?P<name>\w+) has flow rate=(?P<flow_rate>\d+); tunnels? leads? to "
    r"valves? (?P<links>.*)"
)


class Node:
    def __init__(self, name: str, links: list[str], flow_rate: int):
        self.name = name
        self.links = links
        self.flow_rate = flow_rate

    def close(self, time: int) -> int:
        flow_rate = self.flow_rate
        self.flow_rate = 0
        return time * flow_rate

    def get_total_pressure(self, time: int) -> tuple[int, int]:
        return (time - 1) * self.flow_rate, time - 1

    def __repr__(self) -> str:
        return f"Node({self.name!r}, {self.flow_rate!r})"

    def copy(self) -> Node:
        return Node(self.name, self.links.copy(), self.flow_rate)


def parse(s: str) -> dict[str, Node]:
    nodes = {}
    for line in s.splitlines():
        m = node_re.match(line)
        if m is None:
            raise ValueError(f"Invalid input line: {line!r}")
        name = m.group("name")
        flow_rate = int(m.group("flow_rate"))
        links = m.group("links").split(", ")
        nodes[name] = Node(name, links, flow_rate)
    return nodes


def get_distances(nodes: dict[str, Node], cur: str) -> dict[str, int]:
    distances = {cur: 0}
    queue = deque([cur])
    while queue:
        cur = queue.popleft()
        cur_node = nodes[cur]
        for link in cur_node.links:
            if link not in distances:
                distances[link] = distances[cur] + 1
                queue.append(link)
    return distances


def get_pressure_release(
    nodes: dict[str, Node], cur: str, time: int
) -> dict[str, tuple[int, int]]:
    distances = get_distances(nodes, cur)
    pressure_release = {}
    for name, distance in distances.items():
        pressure_release[name] = nodes[name].flow_rate, time - distance - 1
    return pressure_release


def get_best_choice(
    nodes: dict[str, Node], cur: str, time: int, path: str = ""
) -> tuple[str, int]:
    best_pressure = 0
    pressure_release = get_pressure_release(nodes, cur, time)
    choices = [
        (name, pressure * time, time)
        for name, (pressure, time) in pressure_release.items()
        if time > 0 and pressure > 0
    ]
    choices.sort(key=lambda x: x[1], reverse=True)

    if not choices:
        return "", 0

    for name, _, newtime in choices:
        nextnodes = {k: v.copy() for k, v in nodes.items()}
        extra_pressure = nextnodes[name].close(newtime)
        potential = extra_pressure + pressure_release_potential(
            get_pressure_release(nextnodes, name, newtime)
        )

        if potential <= best_pressure:
            continue
        newname, new_pressure = get_best_choice(
            nextnodes, name, newtime, f"{path} -> {name}"
        )
        total_pressure = extra_pressure + new_pressure

        if total_pressure > best_pressure:
            best_pressure = total_pressure
            best_name = name
            print(f"{path:40}: {name} {total_pressure}", file=sys.stderr)

    return best_name, best_pressure


def pressure_release_potential(releases: dict[str, tuple[int, int]]) -> int:
    releases_list = list(releases.values())
    releases_list.sort(key=lambda x: x[0] * x[1], reverse=True)
    dtime = 0
    potential = 0
    for pressure, time in releases_list:
        potential += pressure * (time - dtime)
        dtime -= 1
        if time - dtime <= 0:
            break
    return potential


def compute(s: str) -> int:
    nodes = parse(s)
    time = 30
    cur = "AA"
    _, total_pressure = get_best_choice(nodes, cur, time)
    return total_pressure


INPUT_S = """\
Valve AA has flow rate=0; tunnels lead to valves DD, II, BB
Valve BB has flow rate=13; tunnels lead to valves CC, AA
Valve CC has flow rate=2; tunnels lead to valves DD, BB
Valve DD has flow rate=20; tunnels lead to valves CC, AA, EE
Valve EE has flow rate=3; tunnels lead to valves FF, DD
Valve FF has flow rate=0; tunnels lead to valves EE, GG
Valve GG has flow rate=0; tunnels lead to valves FF, HH
Valve HH has flow rate=22; tunnel leads to valve GG
Valve II has flow rate=0; tunnels lead to valves AA, JJ
Valve JJ has flow rate=21; tunnel leads to valve II
"""
EXPECTED = 1651


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

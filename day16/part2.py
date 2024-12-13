from __future__ import annotations

import argparse
import os.path
import re
from collections import deque
from dataclasses import dataclass
from typing import Iterable

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


@dataclass
class ReducedNode:
    name: str
    links: dict[str, int]
    flow_rate: int

    def invert_links(self) -> dict[int, list[str]]:
        inverted: dict[int, list[str]] = {}
        for name, distance in self.links.items():
            inverted.setdefault(distance, []).append(name)
        return inverted

    def __repr__(self) -> str:
        return f"ReducedNode({self.name!r}, {self.flow_rate!r} {self.invert_links()!r})"


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


def reduce_graph(
    nodes: dict[str, Node], start: Iterable[str]
) -> dict[str, ReducedNode]:
    essential_nodes = [node.name for node in nodes.values() if node.flow_rate > 0]
    reduced_nodes = {
        name: ReducedNode(
            name,
            {
                k: v + 1
                for k, v in get_distances(nodes, name).items()
                if k in essential_nodes and k != name
            },
            nodes[name].flow_rate,
        )
        for name in essential_nodes + list(set(start))
    }
    return reduced_nodes


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
    nodes: dict[str, Node], curs: list[str], times: list[int], path: str = ""
) -> tuple[str, int]:
    worker = times.index(max(times))
    # other = 1 - worker
    time = max(times)
    cur = curs[worker]
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
        # other_potential = extra_pressure + pressure_release_potential(
        #     get_pressure_release(nextnodes, curs[other], times[other])
        # )
        newtimes = times.copy()
        newtimes[worker] = newtime
        newcurs = curs.copy()
        newcurs[worker] = name

        if best_pressure > 0 and len(path) <= 6:
            continue

        if potential <= best_pressure:
            continue
        newname, new_pressure = get_best_choice(
            nextnodes, newcurs, newtimes, f"{path} -> {name}"
        )
        total_pressure = extra_pressure + new_pressure

        if total_pressure > best_pressure:
            best_pressure = total_pressure
            best_name = name
            # print(f"{path:40}: {name} {total_pressure}")

    return best_name, best_pressure


def pressure_release_potential(releases: dict[str, tuple[int, int]]) -> int:
    releases_list = list(releases.values())
    releases_list.sort(key=lambda x: x[0] * x[1], reverse=True)
    dtime = 0
    potential = 0
    for pressure, time in releases_list:
        potential += pressure * (time - dtime // 2)
        dtime -= 1
        if time - dtime <= 0:
            break
    return potential


def score_path(
    nodes: dict[str, ReducedNode], path: list[list[str]], times: list[int]
) -> int:
    score = 0
    for worker_path, time in zip(path, times):
        cur = worker_path[0]
        for next in worker_path[1:]:
            time -= nodes[cur].links[next]
            cur = next
            score += nodes[cur].flow_rate * time
    return score


# def generate_paths(
#     nodes: dict[str, ReducedNode], path: list[list[str]], time: list[int]
# ) -> Iterator[list[list[str]]]:
#     visited = set(w for wp in path for w in wp)
#     for worker, worker_path in enumerate(path):
#         cur = worker_path[-1]
#         options = (
#             n for n, dist in nodes[cur].links.items() - visited if dist < time[worker]
#         )

#         for next in options:
#             new_path = [wp.copy() for wp in path]
#             new_path[worker].append(next)
#             new_time = time.copy()
#             new_time[worker] -= nodes[cur].links[next]
#             yield from generate_paths(nodes, new_path, new_time)

#     yield path


def compute(s: str) -> int:
    nodes = parse(s)
    start = ["AA", "AA"]
    time = [26, 26]
    red_nodes = reduce_graph(nodes, start)
    print(len(red_nodes), red_nodes)
    _, total_pressure = get_best_choice(nodes, start, time)
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
EXPECTED = 1707


@pytest.mark.parametrize(
    ("input_s", "expected"),
    ((INPUT_S, EXPECTED),),
)
def test(input_s: str, expected: int) -> None:
    assert compute(input_s) == expected


@pytest.fixture
def red_nodes() -> dict[str, ReducedNode]:
    return reduce_graph(parse(INPUT_S), ("AA", "AA"))


@pytest.mark.parametrize(
    ("path", "times", "expected"),
    (
        ([["AA", "DD", "BB", "JJ", "HH", "EE", "CC"]], [30], 1651),
        ([["AA", "JJ", "BB", "CC"], ["AA", "DD", "HH", "EE"]], [26, 26], 1707),
    ),
)
def test_score_path(
    red_nodes: dict[str, ReducedNode],
    path: list[list[str]],
    times: list[int],
    expected: int,
) -> None:
    assert score_path(red_nodes, path, times) == expected


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("data_file", nargs="?", default=INPUT_TXT)
    args = parser.parse_args()

    with open(args.data_file) as f, support.timing():  # type: ignore[attr-defined]
        print(compute(f.read()))

    return 0


if __name__ == "__main__":
    raise SystemExit(main())

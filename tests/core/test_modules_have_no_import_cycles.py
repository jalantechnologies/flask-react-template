import ast
import unittest
from pathlib import Path
from typing import Iterable, Optional

BACKEND_ROOT = Path(__file__).resolve().parents[2] / "src" / "apps" / "backend"
MODULES_ROOT = BACKEND_ROOT / "modules"
MODULES_PACKAGE = "modules"
FOUNDATION_MODULE = "core"

KNOWN_CYCLES: frozenset[tuple[str, ...]] = frozenset(
    {
        ("account", "authentication"),
        ("account", "authentication", "notification"),
        ("account", "notification"),
        ("config", "core"),
        ("config", "core", "logger"),
    }
)

KNOWN_FOUNDATION_IMPORTS: frozenset[str] = frozenset({"config", "logger"})


ModuleGraph = dict[str, dict[str, set[str]]]


def _module_name_of(source_file: Path) -> Optional[str]:
    relative_parts = source_file.relative_to(MODULES_ROOT).parts
    if len(relative_parts) < 2:
        return None
    return relative_parts[0]


def _imported_module_paths(source_file: Path) -> Iterable[str]:
    tree = ast.parse(source_file.read_text(encoding="utf-8"), filename=str(source_file))
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            yield from (alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.level == 0 and node.module is not None:
            yield node.module


def _imported_module_name(dotted_path: str) -> Optional[str]:
    parts = dotted_path.split(".")
    if len(parts) < 2 or parts[0] != MODULES_PACKAGE:
        return None
    return parts[1]


def _build_module_graph() -> ModuleGraph:
    graph: ModuleGraph = {}
    for source_file in sorted(MODULES_ROOT.rglob("*.py")):
        importing_module = _module_name_of(source_file)
        if importing_module is None:
            continue
        graph.setdefault(importing_module, {})
        for dotted_path in _imported_module_paths(source_file):
            imported_module = _imported_module_name(dotted_path)
            if imported_module is None or imported_module == importing_module:
                continue
            location = f"{source_file.relative_to(BACKEND_ROOT)}"
            graph[importing_module].setdefault(imported_module, set()).add(location)
    return graph


def _canonical_cycle(cycle: tuple[str, ...]) -> tuple[str, ...]:
    lowest_index = cycle.index(min(cycle))
    return cycle[lowest_index:] + cycle[:lowest_index]


def _find_cycles(graph: ModuleGraph) -> set[tuple[str, ...]]:
    cycles: set[tuple[str, ...]] = set()

    def walk(start: str, current: str, path: tuple[str, ...], visited: frozenset[str]) -> None:
        for neighbour in sorted(graph.get(current, {})):
            if neighbour == start:
                cycles.add(path)
            elif neighbour > start and neighbour not in visited:
                walk(start, neighbour, path + (neighbour,), visited | {neighbour})

    for module_name in sorted(graph):
        walk(module_name, module_name, (module_name,), frozenset({module_name}))
    return cycles


def _describe_cycle(cycle: tuple[str, ...], graph: ModuleGraph) -> str:
    hops = cycle + (cycle[0],)
    arrow_chain = " -> ".join(hops)
    edge_lines = []
    for importing_module, imported_module in zip(hops, hops[1:]):
        locations = sorted(graph.get(importing_module, {}).get(imported_module, set()))
        edge_lines.append(f"    {importing_module} -> {imported_module}: {', '.join(locations)}")
    return f"  {arrow_chain}\n" + "\n".join(edge_lines)


class TestModulesHaveNoImportCycles(unittest.TestCase):
    def setUp(self) -> None:
        self.graph = _build_module_graph()

    def test_foundation_module_imports_no_other_module(self) -> None:
        imported_modules = set(self.graph.get(FOUNDATION_MODULE, {}))
        unexpected = imported_modules - KNOWN_FOUNDATION_IMPORTS

        assert not unexpected, (
            f"'{MODULES_PACKAGE}.{FOUNDATION_MODULE}' is the foundation every other module is built on, so it must "
            f"not import from any module under '{MODULES_PACKAGE}'. These imports are new:\n"
            + "\n".join(
                f"  {FOUNDATION_MODULE} -> {imported_module}: "
                f"{', '.join(sorted(self.graph[FOUNDATION_MODULE][imported_module]))}"
                for imported_module in sorted(unexpected)
            )
            + f"\nMove what '{FOUNDATION_MODULE}' needs into '{FOUNDATION_MODULE}' itself, or pass it in from the "
            f"caller, rather than reaching upward. Do not add it to KNOWN_FOUNDATION_IMPORTS: that list only shrinks."
        )

    def test_modules_take_part_in_no_import_cycle(self) -> None:
        cycles = {_canonical_cycle(cycle) for cycle in _find_cycles(self.graph)}
        unexpected = cycles - KNOWN_CYCLES

        assert not unexpected, (
            "modules must import in one direction, but these cycles exist:\n"
            + "\n".join(_describe_cycle(cycle, self.graph) for cycle in sorted(unexpected))
            + "\nBreak a cycle by moving the shared type into the module both sides already depend on, or by having "
            "the lower module accept what it needs as an argument instead of importing the higher one. Do not add "
            "the cycle to KNOWN_CYCLES: that list only shrinks."
        )


class TestKnownImportCyclesStillExist(unittest.TestCase):
    def setUp(self) -> None:
        self.graph = _build_module_graph()

    def test_every_known_cycle_still_exists(self) -> None:
        cycles = {_canonical_cycle(cycle) for cycle in _find_cycles(self.graph)}
        fixed = KNOWN_CYCLES - cycles

        assert not fixed, (
            "these cycles are listed in KNOWN_CYCLES but no longer exist:\n"
            + "\n".join(f"  {' -> '.join(cycle + (cycle[0],))}" for cycle in sorted(fixed))
            + "\nThey have been fixed, so delete them from KNOWN_CYCLES in this file. The list is a ratchet that "
            "only shrinks, and keeping a fixed cycle listed would let the same cycle come back unnoticed."
        )

    def test_every_known_foundation_import_still_exists(self) -> None:
        imported_modules = set(self.graph.get(FOUNDATION_MODULE, {}))
        fixed = KNOWN_FOUNDATION_IMPORTS - imported_modules

        assert not fixed, (
            f"'{FOUNDATION_MODULE}' no longer imports these modules listed in KNOWN_FOUNDATION_IMPORTS: "
            f"{', '.join(sorted(fixed))}.\nDelete them from KNOWN_FOUNDATION_IMPORTS in this file. The list is a "
            "ratchet that only shrinks, and keeping a fixed entry listed would let the import come back unnoticed."
        )

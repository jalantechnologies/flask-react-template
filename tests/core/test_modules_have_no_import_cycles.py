import ast
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory
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


def _module_name_of(source_file: Path, modules_root: Path = MODULES_ROOT) -> Optional[str]:
    relative_parts = source_file.relative_to(modules_root).parts
    if len(relative_parts) < 2:
        return None
    return relative_parts[0]


def _package_parts_of(source_file: Path, modules_root: Path) -> tuple[str, ...]:
    relative_parts = source_file.relative_to(modules_root).parts
    return (MODULES_PACKAGE,) + relative_parts[:-1]


def _absolute_path_of_relative_import(node: ast.ImportFrom, package_parts: tuple[str, ...]) -> Optional[str]:
    levels_up = node.level - 1
    if levels_up > len(package_parts):
        return None
    anchor = package_parts[: len(package_parts) - levels_up] if levels_up else package_parts
    trailing = tuple(node.module.split(".")) if node.module else ()
    return ".".join(anchor + trailing)


def _imported_module_paths(source_file: Path, modules_root: Path = MODULES_ROOT) -> Iterable[str]:
    tree = ast.parse(source_file.read_text(encoding="utf-8"), filename=str(source_file))
    package_parts = _package_parts_of(source_file, modules_root)
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            yield from (alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom):
            if node.level == 0:
                if node.module is not None:
                    yield node.module
                continue
            absolute_path = _absolute_path_of_relative_import(node, package_parts)
            if absolute_path is not None:
                yield absolute_path


def _imported_module_name(dotted_path: str) -> Optional[str]:
    parts = dotted_path.split(".")
    if len(parts) < 2 or parts[0] != MODULES_PACKAGE:
        return None
    return parts[1]


def _build_module_graph(modules_root: Path = MODULES_ROOT, display_root: Path = BACKEND_ROOT) -> ModuleGraph:
    graph: ModuleGraph = {}
    for source_file in sorted(modules_root.rglob("*.py")):
        importing_module = _module_name_of(source_file, modules_root)
        if importing_module is None:
            continue
        graph.setdefault(importing_module, {})
        for dotted_path in _imported_module_paths(source_file, modules_root):
            imported_module = _imported_module_name(dotted_path)
            if imported_module is None or imported_module == importing_module:
                continue
            location = f"{source_file.relative_to(display_root)}"
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


class TestRelativeImportsCountAsEdges(unittest.TestCase):
    def setUp(self) -> None:
        self.tree = TemporaryDirectory()
        self.addCleanup(self.tree.cleanup)
        self.modules_root = Path(self.tree.name) / MODULES_PACKAGE

    def _write(self, relative_path: str, source: str) -> None:
        source_file = self.modules_root / relative_path
        source_file.parent.mkdir(parents=True, exist_ok=True)
        source_file.write_text(source, encoding="utf-8")

    def _graph(self) -> ModuleGraph:
        return _build_module_graph(self.modules_root, self.modules_root.parent)

    def test_relative_import_of_another_module_is_an_edge(self) -> None:
        self._write("alpha/alpha_service.py", "from ..beta.beta_service import BetaService\n")
        self._write("beta/beta_service.py", "class BetaService:\n    pass\n")

        assert set(self._graph()["alpha"]) == {"beta"}

    def test_relative_import_within_the_same_module_is_not_an_edge(self) -> None:
        self._write("alpha/alpha_service.py", "from .internal.alpha_reader import AlphaReader\n")
        self._write("alpha/internal/alpha_reader.py", "class AlphaReader:\n    pass\n")

        assert self._graph()["alpha"] == {}

    def test_relative_import_from_a_nested_package_reaches_another_module(self) -> None:
        self._write("alpha/internal/alpha_reader.py", "from ...beta.beta_service import BetaService\n")
        self._write("beta/beta_service.py", "class BetaService:\n    pass\n")

        assert set(self._graph()["alpha"]) == {"beta"}

    def test_relative_imports_form_a_detectable_cycle(self) -> None:
        self._write("alpha/alpha_service.py", "from ..beta.beta_service import BetaService\n")
        self._write("beta/beta_service.py", "from ..alpha.alpha_service import AlphaService\n")

        cycles = {_canonical_cycle(cycle) for cycle in _find_cycles(self._graph())}

        assert cycles == {("alpha", "beta")}

    def test_relative_import_escaping_the_modules_package_is_ignored(self) -> None:
        self._write("alpha/alpha_service.py", "from ....somewhere import Thing\n")

        assert self._graph()["alpha"] == {}


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

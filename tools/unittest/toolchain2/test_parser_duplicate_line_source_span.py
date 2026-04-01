from __future__ import annotations

import sys
import unittest
from pathlib import Path


ROOT = next(p for p in Path(__file__).resolve().parents if (p / "src").exists())
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
if str(ROOT / "src") not in sys.path:
    sys.path.insert(0, str(ROOT / "src"))


from toolchain2.compile.lower import lower_east2_to_east3
from toolchain2.parse.py.parser import parse_python_source
from toolchain2.resolve.py.builtin_registry import BuiltinRegistry, load_builtin_registry
from toolchain2.resolve.py.resolver import resolve_east1_to_east2


def _load_registry() -> BuiltinRegistry:
    return load_builtin_registry(
        ROOT / "test" / "include" / "east1" / "py" / "built_in" / "builtins.py.east1",
        ROOT / "test" / "include" / "east1" / "py" / "built_in" / "containers.py.east1",
        ROOT / "test" / "include" / "east1" / "py" / "std",
    )


class ParserDuplicateLineSourceSpanTests(unittest.TestCase):
    def test_duplicate_line_text_does_not_reverse_if_source_span(self) -> None:
        source = """\
def first(flag: bool) -> bool:
    if flag:
        return True
    return False

def second(flag: bool) -> bool:
    if flag:
        return True
    return False
"""
        east1 = parse_python_source(source, filename="<duplicate-lines>").to_jv()
        resolve_east1_to_east2(east1, registry=_load_registry())
        east3 = lower_east2_to_east3(east1)
        for node in self._walk(east3):
            span = node.get("source_span")
            if not isinstance(span, dict):
                continue
            start_line = span.get("lineno")
            end_line = span.get("end_lineno")
            start_col = span.get("col_offset")
            end_col = span.get("end_col_offset")
            if not all(isinstance(v, int) for v in (start_line, end_line, start_col, end_col)):
                continue
            self.assertGreaterEqual(end_line, start_line)
            if end_line == start_line:
                self.assertGreaterEqual(end_col, start_col)

        second_fn = next(node for node in east1["body"] if node.get("kind") == "FunctionDef" and node.get("name") == "second")
        second_if = second_fn["body"][0]
        self.assertEqual(second_if["kind"], "If")
        self.assertEqual(second_if["source_span"]["lineno"], 7)
        self.assertEqual(second_if["source_span"]["end_lineno"], 8)

    def _walk(self, node: object) -> list[dict[str, object]]:
        out: list[dict[str, object]] = []
        if isinstance(node, dict):
            out.append(node)
            for value in node.values():
                out.extend(self._walk(value))
        elif isinstance(node, list):
            for item in node:
                out.extend(self._walk(item))
        return out


if __name__ == "__main__":
    unittest.main()

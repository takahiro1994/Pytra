from __future__ import annotations

import unittest
from pathlib import Path

from toolchain.parse.py.parser import parse_python_source
from toolchain.resolve.py.builtin_registry import load_builtin_registry
from toolchain.resolve.py.resolver import resolve_east1_to_east2


class CallableParamRefinementTests(unittest.TestCase):
    def test_callable_higher_order_refines_callable_params(self) -> None:
        src = Path("/workspace/Pytra/test/fixture/source/py/typing/callable_higher_order.py").read_text(encoding="utf-8")
        doc = parse_python_source(src, "test/fixture/source/py/typing/callable_higher_order.py").to_jv()
        resolve_east1_to_east2(doc, registry=load_builtin_registry())

        functions: dict[str, dict[str, object]] = {}
        for stmt in doc.get("body", []):
            if isinstance(stmt, dict) and stmt.get("kind") == "FunctionDef":
                name = stmt.get("name")
                if isinstance(name, str):
                    functions[name] = stmt

        self.assertEqual(functions["compose"]["arg_types"]["f"], "callable[[int64],int64]")
        self.assertEqual(functions["compose"]["arg_types"]["g"], "callable[[int64],int64]")
        self.assertEqual(functions["apply_twice"]["arg_types"]["fn"], "callable[[int64],int64]")
        self.assertEqual(functions["apply_to_list"]["arg_types"]["fn"], "callable[[int64],int64]")


if __name__ == "__main__":
    unittest.main()

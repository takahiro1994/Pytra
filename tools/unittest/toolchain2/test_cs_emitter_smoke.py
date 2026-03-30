from __future__ import annotations

import unittest

from toolchain2.compile.lower import lower_east2_to_east3
from toolchain2.emit.cs.emitter import emit_cs_module


class CSharpEmitterSmokeTests(unittest.TestCase):
    def test_emit_cs_module_renders_basic_function(self) -> None:
        east2 = {
            "kind": "Module",
            "body": [
                {
                    "kind": "FunctionDef",
                    "name": "add_one",
                    "args": [{"arg": "x", "resolved_type": "int64"}],
                    "arg_types": {"x": "int64"},
                    "arg_order": ["x"],
                    "arg_defaults": {},
                    "arg_index": {"x": 0},
                    "return_type": "int64",
                    "arg_usage": {"x": "readonly"},
                    "renamed_symbols": {},
                    "docstring": None,
                    "body": [
                        {
                            "kind": "Return",
                            "value": {
                                "kind": "BinOp",
                                "op": "Add",
                                "resolved_type": "int64",
                                "left": {"kind": "Name", "id": "x", "resolved_type": "int64"},
                                "right": {"kind": "Constant", "value": 1, "resolved_type": "int64"},
                            },
                        }
                    ],
                }
            ],
            "main_guard_body": [],
        }

        east3 = lower_east2_to_east3(east2, target_language="cs")
        east3["meta"] = {
            "emit_context": {"module_id": "sample.basic", "is_entry": False},
            "linked_program_v1": {"module_id": "sample.basic"},
        }
        code = emit_cs_module(east3)

        self.assertIn("namespace Pytra.CsModule", code)
        self.assertIn("public static class Basic", code)
        self.assertIn("public static long add_one(long x)", code)
        self.assertIn("return x + 1;", code)

    def test_emit_cs_module_resolves_runtime_call(self) -> None:
        east3 = {
            "kind": "Module",
            "body": [],
            "main_guard_body": [
                {
                    "kind": "Expr",
                    "value": {
                        "kind": "Call",
                        "resolved_type": "None",
                        "runtime_call": "py_print",
                        "runtime_call_adapter_kind": "builtin",
                        "func": {"kind": "Name", "id": "print", "resolved_type": "callable"},
                        "args": [{"kind": "Constant", "value": "hello", "resolved_type": "str"}],
                        "keywords": [],
                    },
                }
            ],
            "meta": {
                "emit_context": {"module_id": "sample.entry", "is_entry": True},
                "linked_program_v1": {"module_id": "sample.entry"},
            },
        }

        code = emit_cs_module(east3)

        self.assertIn("public static void Main(string[] args)", code)
        self.assertIn("py_runtime.py_print(\"hello\");", code)


if __name__ == "__main__":
    unittest.main()

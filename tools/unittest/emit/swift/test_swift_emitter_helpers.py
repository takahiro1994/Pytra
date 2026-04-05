from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path


ROOT = next(p for p in Path(__file__).resolve().parents if (p / "src").exists())
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
if str(ROOT / "src") not in sys.path:
    sys.path.insert(0, str(ROOT / "src"))

_EMITTER_PATH = ROOT / "src" / "toolchain" / "emit" / "swift" / "emitter.py"
_SPEC = importlib.util.spec_from_file_location("swift_emitter_mod", str(_EMITTER_PATH))
if _SPEC is None or _SPEC.loader is None:
    raise RuntimeError("failed to load swift emitter module spec")
swift_emitter_mod = importlib.util.module_from_spec(_SPEC)
_SPEC.loader.exec_module(swift_emitter_mod)


class SwiftEmitterHelpersTest(unittest.TestCase):
    def test_scan_reassigned_names_ignores_non_string_kind_values(self) -> None:
        out: set[str] = set()
        swift_emitter_mod._scan_reassigned_names(
            {
                "kind": ["not-a-node-kind"],
                "body": [
                    {
                        "kind": "Assign",
                        "target": {"kind": "Name", "id": "value"},
                    }
                ],
            },
            {"value"},
            out,
        )
        self.assertEqual(out, {"value"})

    def test_emit_runtime_iter_target_bindings_supports_nested_tuple_targets(self) -> None:
        ctx = {"tmp": 0}
        body_ctx = {"declared": set(), "types": {}}
        lines = swift_emitter_mod._emit_runtime_iter_target_bindings(
            {
                "kind": "TupleTarget",
                "elements": [
                    {"kind": "NameTarget", "id": "name", "target_type": "str"},
                    {
                        "kind": "TupleTarget",
                        "elements": [
                            {"kind": "NameTarget", "id": "had_local", "target_type": "bool"},
                            {"kind": "NameTarget", "id": "value", "target_type": "str"},
                        ],
                        "target_type": "tuple[bool,str]",
                    },
                ],
                "target_type": "tuple[str,tuple[bool,str]]",
            },
            "iterValue",
            indent="    ",
            ctx=ctx,
            body_ctx=body_ctx,
        )
        rendered = "\n".join(lines)
        self.assertIn("let __tuple_", rendered)
        self.assertIn("let name: String", rendered)
        self.assertIn("let had_local: Bool", rendered)
        self.assertIn("let value: String", rendered)
        self.assertEqual(body_ctx["declared"], {"name", "had_local", "value"})


if __name__ == "__main__":
    unittest.main()

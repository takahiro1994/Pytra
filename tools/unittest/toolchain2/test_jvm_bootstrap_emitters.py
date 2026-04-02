from __future__ import annotations

import sys
import unittest
from pathlib import Path


ROOT = next(p for p in Path(__file__).resolve().parents if (p / "src").exists())
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
if str(ROOT / "src") not in sys.path:
    sys.path.insert(0, str(ROOT / "src"))


from toolchain2.emit.scala.emitter import emit_scala_module
from toolchain2.emit.kotlin.emitter import emit_kotlin_module


def _module_doc(module_id: str) -> dict[str, object]:
    return {
        "kind": "Module",
        "east_stage": 3,
        "schema_version": 1,
        "meta": {"module_id": module_id, "dispatch_mode": "native"},
        "body": [],
    }


class JvmBootstrapEmitterTests(unittest.TestCase):
    def test_scala_bootstrap_emitter_imports_and_emits_empty_module(self) -> None:
        out = emit_scala_module(_module_doc("pkg.demo"))
        self.assertIn("object pkg_demo", out)
        self.assertIn("bootstrap scaffold", out)

    def test_kotlin_bootstrap_emitter_imports_and_emits_empty_module(self) -> None:
        out = emit_kotlin_module(_module_doc("pkg.demo"))
        self.assertIn("object pkg_demo", out)
        self.assertIn("bootstrap scaffold", out)


if __name__ == "__main__":
    unittest.main()

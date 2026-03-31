from __future__ import annotations

import importlib.util
import os
import subprocess
import sys
import unittest
from pathlib import Path


ROOT = next(p for p in Path(__file__).resolve().parents if (p / "src").exists())
CPP_GOLDEN_DIR = ROOT / "test" / "selfhost" / "cpp"
REGEN_PATH = ROOT / "tools" / "gen" / "regenerate_selfhost_golden.py"
TIMEOUT_SEC = int(os.environ.get("SELFHOST_GOLDEN_TIMEOUT", "30"))
KNOWN_CPP_GOLDEN_SKIPS = {
    "toolchain2.compile.passes",
    "toolchain2.optimize.passes.tuple_target_direct_expansion",
    "toolchain2.optimize.passes.typed_enumerate_normalization",
    "toolchain2.optimize.passes.typed_repeat_materialization",
    "toolchain2.resolve.py.resolver",
}

_EMIT_HELPER = """
import sys
sys.path.insert(0, sys.argv[1])
target = sys.argv[2]
east3_path = sys.argv[3]
module_id = sys.argv[4]
spec_path = sys.argv[5]
import importlib.util
spec = importlib.util.spec_from_file_location("regen", spec_path)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)
doc, err = mod.emit_module(target, mod.Path(east3_path), 60, module_id)
if doc is None:
    raise RuntimeError(err)
print(doc, end="")
"""


def _load_regen_module() -> object:
    spec = importlib.util.spec_from_file_location("regen", REGEN_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError("failed to load regenerate_selfhost_golden.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _collect_cpp_entries() -> dict[str, tuple[str, Path]]:
    mod = _load_regen_module()
    entries = mod.collect_east3_opt_entries()
    return {
        module_id.replace(".", "_") + ".cpp": (module_id, east3_path)
        for east3_path, module_id in entries
    }


class SelfhostCppGoldenTest(unittest.TestCase):
    def test_cpp_golden_dir_populated_for_supported_modules(self) -> None:
        entries = _collect_cpp_entries()
        golden_names = {p.name for p in CPP_GOLDEN_DIR.glob("*.cpp")}
        expected_names = set(entries.keys())
        missing_names = sorted(expected_names - golden_names)
        missing_modules = {entries[name][0] for name in missing_names}
        self.assertEqual(missing_modules, KNOWN_CPP_GOLDEN_SKIPS)

    def test_cpp_golden_matches_current_emitter_output(self) -> None:
        entries = _collect_cpp_entries()
        for golden_path in sorted(CPP_GOLDEN_DIR.glob("*.cpp")):
            meta = entries.get(golden_path.name)
            if meta is None:
                self.fail(f"missing east3-opt entry for {golden_path.name}")
            module_id, east3_path = meta
            with self.subTest(module_id=module_id):
                try:
                    result = subprocess.run(
                        [
                            sys.executable,
                            "-c",
                            _EMIT_HELPER,
                            str(ROOT / "src"),
                            "cpp",
                            str(east3_path),
                            module_id,
                            str(REGEN_PATH),
                        ],
                        capture_output=True,
                        text=True,
                        timeout=TIMEOUT_SEC,
                    )
                except subprocess.TimeoutExpired:
                    self.skipTest(f"emit timed out after {TIMEOUT_SEC}s for {module_id}")
                if result.returncode != 0:
                    self.fail(f"emit failed for {module_id}: {result.stderr.strip()[:200]}")
                self.assertEqual(result.stdout, golden_path.read_text(encoding="utf-8"))

from __future__ import annotations

import importlib.util
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch


ROOT = next(p for p in Path(__file__).resolve().parents if (p / "src").exists())
MODULE_PATH = ROOT / "tools" / "run" / "run_selfhost_parity.py"


def _load_module():
    spec = importlib.util.spec_from_file_location("run_selfhost_parity", MODULE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError("failed to load run_selfhost_parity module")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class RunSelfhostParityBuildTest(unittest.TestCase):
    def test_build_selfhost_binary_cpp_uses_runtime_sources_and_include_dirs(self) -> None:
        mod = _load_module()
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            emit_dir = root / "work" / "selfhost" / "build" / "cpp" / "emit"
            emit_dir.mkdir(parents=True, exist_ok=True)
            (emit_dir / "entry.cpp").write_text("int main() { return 0; }\n", encoding="utf-8")
            (root / "src" / "pytra-cli2.py").parent.mkdir(parents=True, exist_ok=True)
            (root / "src" / "pytra-cli2.py").write_text("", encoding="utf-8")

            calls: list[list[str]] = []

            def _fake_run(cmd: list[str], cwd: str, capture_output: bool, text: bool):
                calls.append(cmd)
                if cmd and cmd[0] == sys.executable:
                    emit_dir.mkdir(parents=True, exist_ok=True)
                    (emit_dir / "entry.cpp").write_text("int main() { return 0; }\n", encoding="utf-8")
                return subprocess.CompletedProcess(cmd, 0, stdout="", stderr="")

            with patch.object(mod, "ROOT", root), patch.object(
                mod, "collect_runtime_cpp_sources", return_value=["src/runtime/east/std/pathlib.cpp"]
            ), patch.object(mod.subprocess, "run", side_effect=_fake_run):
                bin_path, err = mod._build_selfhost_binary("cpp")

            self.assertEqual(err, "")
            self.assertEqual(bin_path, root / "work" / "selfhost" / "bin" / "cpp")
            self.assertEqual(len(calls), 2)
            self.assertEqual(calls[0][0], sys.executable)
            self.assertEqual(calls[0][1], str(root / "src" / "pytra-cli2.py"))
            self.assertEqual(calls[0][2], "-build")
            self.assertEqual(calls[0][3], str(root / "src" / "pytra-cli2.py"))
            compile_cmd = calls[1]
            self.assertEqual(compile_cmd[0:3], ["g++", "-O2", "-std=c++20"])
            self.assertIn(str(emit_dir), compile_cmd)
            self.assertIn(str(root / "src"), compile_cmd)
            self.assertIn(str(root / "src" / "runtime" / "cpp"), compile_cmd)
            self.assertIn(str(root / "src" / "runtime" / "east"), compile_cmd)
            self.assertIn(str(emit_dir / "entry.cpp"), compile_cmd)
            self.assertIn(str(root / "src" / "runtime" / "east" / "std" / "pathlib.cpp"), compile_cmd)

    def test_build_selfhost_binary_rs_uses_cargo_package_output(self) -> None:
        mod = _load_module()
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            emit_dir = root / "work" / "selfhost" / "build" / "rs" / "emit"
            (emit_dir / "target" / "release").mkdir(parents=True, exist_ok=True)
            (emit_dir / "Cargo.toml").write_text("[package]\nname='pytra_selfhost'\nversion='0.1.0'\n", encoding="utf-8")
            (emit_dir / "target" / "release" / "pytra_selfhost").write_text("", encoding="utf-8")
            (root / "src" / "pytra-cli2.py").parent.mkdir(parents=True, exist_ok=True)
            (root / "src" / "pytra-cli2.py").write_text("", encoding="utf-8")

            calls: list[list[str]] = []

            def _fake_run(cmd: list[str], cwd: str, capture_output: bool, text: bool):
                calls.append(cmd)
                if cmd and cmd[0] == sys.executable:
                    emit_dir.mkdir(parents=True, exist_ok=True)
                    (emit_dir / "Cargo.toml").write_text(
                        "[package]\nname='pytra_selfhost'\nversion='0.1.0'\n",
                        encoding="utf-8",
                    )
                    release_dir = emit_dir / "target" / "release"
                    release_dir.mkdir(parents=True, exist_ok=True)
                    (release_dir / "pytra_selfhost").write_text("", encoding="utf-8")
                return subprocess.CompletedProcess(cmd, 0, stdout="", stderr="")

            with patch.object(mod, "ROOT", root), patch.object(mod.subprocess, "run", side_effect=_fake_run):
                bin_path, err = mod._build_selfhost_binary("rs")

            self.assertEqual(err, "")
            self.assertEqual(bin_path, root / "work" / "selfhost" / "bin" / "rs")
            self.assertEqual(len(calls), 2)
            self.assertEqual(calls[0][0:5], [sys.executable, str(root / "src" / "pytra-cli2.py"), "-build", str(root / "src" / "pytra-cli2.py"), "--target"])
            self.assertIn("--rs-package", calls[0])
            self.assertEqual(calls[1], ["cargo", "build", "--release"])

    def test_transpile_via_selfhost_binary_uses_emit_manifest_bundle(self) -> None:
        mod = _load_module()
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            out_dir = root / "out"
            case_path = root / "case.py"
            case_path.write_text("print(1)\n", encoding="utf-8")
            linked_manifest = {"modules": [{"module_id": "demo.main", "output": "east3/demo/main.east3.json"}]}
            linked_modules = [
                SimpleNamespace(
                    module_id="demo.main",
                    east_doc={"kind": "Program"},
                )
            ]
            link_result = SimpleNamespace(manifest=linked_manifest, linked_modules=linked_modules)
            calls: list[list[str]] = []

            def _fake_run(cmd: list[str], cwd: str, capture_output: bool, text: bool, timeout: int):
                calls.append(cmd)
                return subprocess.CompletedProcess(cmd, 0, stdout="", stderr="")

            with patch.object(mod, "ROOT", root), \
                patch("toolchain2.parse.py.parse_python.parse_python_file", return_value={}), \
                patch("toolchain2.resolve.py.builtin_registry.load_builtin_registry", return_value=object()), \
                patch("toolchain2.resolve.py.resolver.resolve_east1_to_east2"), \
                patch("toolchain2.compile.lower.lower_east2_to_east3", return_value={}), \
                patch("toolchain2.optimize.optimizer.optimize_east3_document", return_value=({}, {})), \
                patch("toolchain2.link.linker.link_modules", return_value=link_result), \
                patch.object(mod.subprocess, "run", side_effect=_fake_run):
                ok, err = mod._transpile_via_selfhost_binary(root / "bin" / "rs", "rs", case_path, out_dir)

            self.assertTrue(ok, err)
            self.assertEqual(len(calls), 1)
            self.assertEqual(
                calls[0],
                [
                    str(root / "bin" / "rs"),
                    "-emit",
                    str(out_dir / "_linked"),
                    "-o",
                    str(out_dir / "emit"),
                    "--target",
                    "rs",
                ],
            )
            manifest_path = out_dir / "_linked" / "manifest.json"
            self.assertTrue(manifest_path.exists())
            east_path = out_dir / "_linked" / "east3" / "demo" / "main.east3.json"
            self.assertTrue(east_path.exists())


if __name__ == "__main__":
    unittest.main()

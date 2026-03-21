"""py2julia (EAST based) smoke tests — transpile + execution."""

from __future__ import annotations

import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = next(p for p in Path(__file__).resolve().parents if (p / "src").exists())
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
if str(ROOT / "src") not in sys.path:
    sys.path.insert(0, str(ROOT / "src"))

from toolchain.emit.julia.emitter import transpile_to_julia, transpile_to_julia_native
from toolchain.misc.transpile_cli import load_east3_document

RUNTIME_SRC = ROOT / "src" / "runtime" / "julia" / "built_in" / "py_runtime.jl"
JULIA_BIN = shutil.which("julia") or ""


def load_east(
    input_path: Path,
    parser_backend: str = "self_hosted",
    east_stage: str = "3",
    object_dispatch_mode: str = "native",
    east3_opt_level: str = "1",
    east3_opt_pass: str = "",
    dump_east3_before_opt: str = "",
    dump_east3_after_opt: str = "",
    dump_east3_opt_trace: str = "",
):
    if east_stage != "3":
        raise RuntimeError("unsupported east_stage: " + east_stage)
    doc3 = load_east3_document(
        input_path,
        parser_backend=parser_backend,
        object_dispatch_mode=object_dispatch_mode,
        east3_opt_level=east3_opt_level,
        east3_opt_pass=east3_opt_pass,
        dump_east3_before_opt=dump_east3_before_opt,
        dump_east3_after_opt=dump_east3_after_opt,
        dump_east3_opt_trace=dump_east3_opt_trace,
        target_lang="julia",
    )
    return doc3 if isinstance(doc3, dict) else {}


def find_fixture_case(stem: str) -> Path:
    matches = sorted((ROOT / "test" / "fixtures").rglob(f"{stem}.py"))
    if not matches:
        raise FileNotFoundError(f"missing fixture: {stem}")
    return matches[0]


def _run_julia(source: str, timeout: int = 15) -> subprocess.CompletedProcess[str]:
    """Write source to a temp dir with runtime and run julia."""
    with tempfile.TemporaryDirectory() as tmpdir:
        src_path = Path(tmpdir) / "main.jl"
        src_path.write_text(source, encoding="utf-8")
        shutil.copy2(str(RUNTIME_SRC), str(Path(tmpdir) / "py_runtime.jl"))
        return subprocess.run(
            [JULIA_BIN, str(src_path)],
            capture_output=True,
            text=True,
            timeout=timeout,
        )


def _transpile_and_run(fixture_stem: str, timeout: int = 15) -> subprocess.CompletedProcess[str]:
    """Transpile a fixture to Julia and run it."""
    east_doc = load_east(find_fixture_case(fixture_stem))
    source = transpile_to_julia_native(east_doc)
    return _run_julia(source, timeout=timeout)


# ── Transpile-only tests ──


class Py2JuliaSmokeTest(unittest.TestCase):
    def test_julia_runtime_exists(self) -> None:
        runtime_path = ROOT / "src" / "runtime" / "julia" / "built_in" / "py_runtime.jl"
        self.assertTrue(runtime_path.exists())

    def test_transpile_simple_add(self) -> None:
        east_doc = load_east(find_fixture_case("add"))
        source = transpile_to_julia_native(east_doc)
        self.assertIsInstance(source, str)
        self.assertIn("function", source)
        self.assertIn("end", source)

    def test_transpile_fib(self) -> None:
        east_doc = load_east(find_fixture_case("fib"))
        source = transpile_to_julia_native(east_doc)
        self.assertIn("function", source)
        self.assertIn("if", source)

    def test_transpile_if_else(self) -> None:
        east_doc = load_east(find_fixture_case("if_else"))
        source = transpile_to_julia_native(east_doc)
        self.assertIn("if", source)
        self.assertIn("end", source)

    def test_transpile_for_loop(self) -> None:
        east_doc = load_east(find_fixture_case("for_range"))
        source = transpile_to_julia_native(east_doc)
        self.assertIn("for", source)
        self.assertIn("end", source)

    def test_transpile_loop(self) -> None:
        east_doc = load_east(find_fixture_case("loop"))
        source = transpile_to_julia_native(east_doc)
        self.assertIn("for", source)
        self.assertIn("end", source)

    def test_transpile_compare(self) -> None:
        east_doc = load_east(find_fixture_case("compare"))
        source = transpile_to_julia_native(east_doc)
        self.assertIsInstance(source, str)

    def test_transpile_dict_literal_entries(self) -> None:
        east_doc = load_east(find_fixture_case("dict_literal_entries"))
        source = transpile_to_julia_native(east_doc)
        self.assertIn("Dict", source)

    def test_transpile_class(self) -> None:
        east_doc = load_east(find_fixture_case("class_body_pass"))
        source = transpile_to_julia_native(east_doc)
        self.assertIn("mutable struct", source)
        self.assertIn("end", source)

    def test_transpile_assign(self) -> None:
        east_doc = load_east(find_fixture_case("assign"))
        source = transpile_to_julia_native(east_doc)
        self.assertIn("=", source)

    def test_transpile_to_julia_api_compat(self) -> None:
        """transpile_to_julia is an alias for transpile_to_julia_native."""
        east_doc = load_east(find_fixture_case("add"))
        source = transpile_to_julia(east_doc)
        self.assertIsInstance(source, str)
        self.assertIn("function", source)


# ── Execution tests (require julia binary) ──


@unittest.skipUnless(JULIA_BIN, "julia not found in PATH")
class Py2JuliaExecTest(unittest.TestCase):
    """Transpile fixtures to Julia and verify execution succeeds."""

    def _assert_runs_ok(self, fixture_stem: str) -> str:
        cp = _transpile_and_run(fixture_stem)
        self.assertEqual(
            cp.returncode, 0,
            f"{fixture_stem}: julia exited {cp.returncode}\nstderr: {cp.stderr[:500]}",
        )
        return cp.stdout

    def test_exec_add(self) -> None:
        self._assert_runs_ok("add")

    def test_exec_fib(self) -> None:
        self._assert_runs_ok("fib")

    def test_exec_assign(self) -> None:
        self._assert_runs_ok("assign")

    def test_exec_compare(self) -> None:
        self._assert_runs_ok("compare")

    def test_exec_float(self) -> None:
        self._assert_runs_ok("float")

    def test_exec_if_else(self) -> None:
        self._assert_runs_ok("if_else")

    def test_exec_for_range(self) -> None:
        self._assert_runs_ok("for_range")

    def test_exec_loop(self) -> None:
        self._assert_runs_ok("loop")

    def test_exec_not(self) -> None:
        self._assert_runs_ok("not")

    def test_exec_lambda_as_arg(self) -> None:
        self._assert_runs_ok("lambda_as_arg")

    def test_exec_lambda_immediate(self) -> None:
        self._assert_runs_ok("lambda_immediate")

    def test_exec_comprehension(self) -> None:
        self._assert_runs_ok("comprehension")

    def test_exec_in_membership(self) -> None:
        self._assert_runs_ok("in_membership")

    def test_exec_negative_index(self) -> None:
        self._assert_runs_ok("negative_index")

    def test_exec_slice_basic(self) -> None:
        self._assert_runs_ok("slice_basic")

    def test_exec_dict_literal_entries(self) -> None:
        self._assert_runs_ok("dict_literal_entries")

    def test_exec_string(self) -> None:
        self._assert_runs_ok("string")

    def test_exec_string_ops(self) -> None:
        self._assert_runs_ok("string_ops")

    def test_exec_class_body_pass(self) -> None:
        self._assert_runs_ok("class_body_pass")

    def test_exec_class_instance(self) -> None:
        self._assert_runs_ok("class_instance")

    def test_exec_class_member(self) -> None:
        self._assert_runs_ok("class_member")

    def test_exec_try_raise(self) -> None:
        self._assert_runs_ok("try_raise")

    def test_exec_finally(self) -> None:
        self._assert_runs_ok("finally")

    def test_exec_ifexp_bool(self) -> None:
        self._assert_runs_ok("ifexp_bool")

    def test_exec_dict_get_items(self) -> None:
        self._assert_runs_ok("dict_get_items")

    def test_exec_list_repeat(self) -> None:
        self._assert_runs_ok("list_repeat")

    def test_exec_comprehension_filter(self) -> None:
        self._assert_runs_ok("comprehension_filter")

    def test_exec_dict_in(self) -> None:
        self._assert_runs_ok("dict_in")


if __name__ == "__main__":
    unittest.main()

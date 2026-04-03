from pytra.std.argparse import ArgumentParser
from pytra.utils.assertions import py_assert_all, py_assert_eq


def run_argparse_extended() -> bool:
    p: ArgumentParser = ArgumentParser("x")
    p.add_argument("input")
    p.add_argument("-o", "--output")
    p.add_argument("--pretty", action="store_true")
    p.add_argument("-m", "--mode", choices=["a", "b"], default="a")
    checks: list[bool] = []
    checks.append(py_assert_eq(str(p.parse_args(["a.py", "-o", "out.cpp", "--pretty", "-m", "b"])["input"]), "a.py", "input"))
    checks.append(py_assert_eq(str(p.parse_args(["a.py", "-o", "out.cpp", "--pretty", "-m", "b"])["output"]), "out.cpp", "output"))
    checks.append(py_assert_eq(bool(p.parse_args(["a.py", "-o", "out.cpp", "--pretty", "-m", "b"])["pretty"]), True, "pretty"))
    checks.append(py_assert_eq(str(p.parse_args(["a.py", "-o", "out.cpp", "--pretty", "-m", "b"])["mode"]), "b", "mode"))
    return py_assert_all(checks, "argparse_extended")


if __name__ == "__main__":
    print(run_argparse_extended())

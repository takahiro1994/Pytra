from pytra.utils.assertions import py_assert_all, py_assert_eq
from pathlib import Path


def run_with_statement() -> bool:
    checks: list[bool] = []

    base = Path("work/transpile/obj/with_stmt_test")
    base.mkdir(parents=True, exist_ok=True)

    # with open(..., "w") as f: f.write(...)
    p = base / "hello.txt"
    with open(str(p), "w") as f:
        f.write("hello with")

    # with open(..., "r") as f: f.read()
    with open(str(p), "r") as f:
        content: str = f.read()
    checks.append(py_assert_eq(content, "hello with", "write_read"))

    # with ... as — multiple sequential with blocks
    p2 = base / "nums.txt"
    with open(str(p2), "w") as f:
        f.write("123")
    with open(str(p2), "r") as f:
        nums: str = f.read()
    checks.append(py_assert_eq(nums, "123", "sequential_with"))

    # with block variable scope — var assigned inside with is accessible outside
    with open(str(p), "r") as f:
        inside: str = f.read()
    checks.append(py_assert_eq(inside, "hello with", "scope_after_with"))

    return py_assert_all(checks, "with_statement")


if __name__ == "__main__":
    print(run_with_statement())

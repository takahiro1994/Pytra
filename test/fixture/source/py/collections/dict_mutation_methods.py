from pytra.utils.assertions import py_assert_all, py_assert_eq


def run_case() -> bool:
    checks: list[bool] = []

    # dict.clear
    d: dict[str, int] = {"a": 1, "b": 2}
    d.clear()
    checks.append(py_assert_eq(len(d), 0, "clear_len"))

    # dict.pop
    e: dict[str, int] = {"x": 10, "y": 20}
    val: int = e.pop("x")
    checks.append(py_assert_eq(val, 10, "pop_val"))
    checks.append(py_assert_eq(len(e), 1, "pop_len"))

    # dict.setdefault
    f: dict[str, int] = {"a": 1}
    r1: int = f.setdefault("a", 99)
    r2: int = f.setdefault("b", 42)
    checks.append(py_assert_eq(r1, 1, "setdefault_existing"))
    checks.append(py_assert_eq(r2, 42, "setdefault_new"))
    checks.append(py_assert_eq(f["b"], 42, "setdefault_stored"))

    return py_assert_all(checks, "dict_mutation_methods")


if __name__ == "__main__":
    print(run_case())

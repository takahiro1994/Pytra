from pytra.utils.assertions import py_assert_all, py_assert_eq


def run_case() -> bool:
    checks: list[bool] = []

    # set.clear
    s: set[int] = {1, 2, 3}
    s.clear()
    checks.append(py_assert_eq(len(s), 0, "clear_len"))

    # set.add
    s.add(10)
    s.add(20)
    checks.append(py_assert_eq(len(s), 2, "add_len"))
    checks.append(py_assert_eq(10 in s, True, "add_in"))

    return py_assert_all(checks, "set_mutation_methods")


if __name__ == "__main__":
    print(run_case())

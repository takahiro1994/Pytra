from pytra.utils.assertions import py_assert_all, py_assert_eq


def run_case() -> bool:
    checks: list[bool] = []

    # list.clear
    a: list[int] = [1, 2, 3]
    a.clear()
    checks.append(py_assert_eq(len(a), 0, "clear_len"))

    # list.sort
    b: list[int] = [3, 1, 4, 1, 5, 9, 2, 6]
    b.sort()
    checks.append(py_assert_eq(b[0], 1, "sort_first"))
    checks.append(py_assert_eq(b[7], 9, "sort_last"))

    # list.reverse
    c: list[int] = [1, 2, 3]
    c.reverse()
    checks.append(py_assert_eq(c[0], 3, "reverse_first"))
    checks.append(py_assert_eq(c[2], 1, "reverse_last"))

    return py_assert_all(checks, "list_mutation_methods")


if __name__ == "__main__":
    print(run_case())

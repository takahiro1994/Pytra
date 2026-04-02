from pytra.utils.assertions import py_assert_all, py_assert_eq, py_assert_true


def run_case() -> bool:
    checks: list[bool] = []

    # str.lower
    s: str = "Hello World"
    checks.append(py_assert_eq(s.lower(), "hello world", "lower"))

    # str.find
    t: str = "abcdef"
    checks.append(py_assert_eq(t.find("cd"), 2, "find_found"))
    checks.append(py_assert_eq(t.find("xy"), -1, "find_not_found"))

    # str.index
    checks.append(py_assert_eq(t.index("cd"), 2, "index_found"))

    # str.isalnum
    checks.append(py_assert_true("abc123".isalnum(), "isalnum_true"))
    checks.append(py_assert_eq("abc!".isalnum(), False, "isalnum_false"))

    # str.lstrip
    u: str = "   hello"
    checks.append(py_assert_eq(u.lstrip(), "hello", "lstrip"))

    # str.split
    v: str = "a,b,c"
    parts: list[str] = v.split(",")
    checks.append(py_assert_eq(len(parts), 3, "split_len"))
    checks.append(py_assert_eq(parts[0], "a", "split_first"))
    checks.append(py_assert_eq(parts[2], "c", "split_last"))

    return py_assert_all(checks, "str_methods_extended")


if __name__ == "__main__":
    print(run_case())

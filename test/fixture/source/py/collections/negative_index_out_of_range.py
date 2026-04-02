from pytra.utils.assertions import py_assert_all, py_assert_true


def run_negative_index_out_of_range() -> bool:
    a: list[int] = [1, 2, 3]
    checks: list[bool] = []

    # a[-100]: normalization gives -97, still out of range → IndexError
    caught_list: bool = False
    try:
        _x: int = a[-100]
    except IndexError:
        caught_list = True
    checks.append(py_assert_true(caught_list, "list[-100] raises IndexError"))

    # str[-100]: same behavior
    s: str = "abc"
    caught_str: bool = False
    try:
        _c: str = s[-100]
    except IndexError:
        caught_str = True
    checks.append(py_assert_true(caught_str, "str[-100] raises IndexError"))

    # a[-1] should NOT raise (valid negative index)
    caught_valid: bool = False
    try:
        _v: int = a[-1]
    except IndexError:
        caught_valid = True
    checks.append(py_assert_true(not caught_valid, "list[-1] does not raise"))

    return py_assert_all(checks, "negative_index_out_of_range")


if __name__ == "__main__":
    print(run_negative_index_out_of_range())

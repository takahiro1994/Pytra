from pytra.utils.assertions import py_assert_all, py_assert_eq


def test_basic_unpack() -> list[bool]:
    """基本の tuple unpack"""
    checks: list[bool] = []
    x, y, z = 1, 2, 3
    checks.append(py_assert_eq(x, 1, "basic_x"))
    checks.append(py_assert_eq(y, 2, "basic_y"))
    checks.append(py_assert_eq(z, 3, "basic_z"))
    return checks


def test_paren_unpack() -> list[bool]:
    """括弧付き tuple unpack — (x, y, z) = (1, 2, 3)"""
    checks: list[bool] = []
    (x, y, z) = (1, 2, 3)
    checks.append(py_assert_eq(x, 1, "paren_x"))
    checks.append(py_assert_eq(y, 2, "paren_y"))
    checks.append(py_assert_eq(z, 3, "paren_z"))
    return checks


def test_bracket_unpack() -> list[bool]:
    """角括弧付き unpack — [x, y, z] = [1, 2, 3]"""
    checks: list[bool] = []
    [x, y, z] = [1, 2, 3]
    checks.append(py_assert_eq(x, 1, "bracket_x"))
    checks.append(py_assert_eq(y, 2, "bracket_y"))
    checks.append(py_assert_eq(z, 3, "bracket_z"))
    return checks


def test_list_rhs_unpack() -> list[bool]:
    """右辺が list の unpack"""
    checks: list[bool] = []
    x, y, z = [10, 20, 30]
    checks.append(py_assert_eq(x, 10, "list_rhs_x"))
    checks.append(py_assert_eq(y, 20, "list_rhs_y"))
    checks.append(py_assert_eq(z, 30, "list_rhs_z"))
    return checks


def test_comprehension_unpack() -> list[bool]:
    """list comprehension の結果を unpack"""
    checks: list[bool] = []
    x, y, z = [i for i in range(3)]
    checks.append(py_assert_eq(x, 0, "comp_x"))
    checks.append(py_assert_eq(y, 1, "comp_y"))
    checks.append(py_assert_eq(z, 2, "comp_z"))
    return checks


def test_function_return_unpack() -> list[bool]:
    """関数の戻り値を unpack"""
    checks: list[bool] = []

    def make_pair() -> tuple[int, str]:
        return (42, "hello")

    n, s = make_pair()
    checks.append(py_assert_eq(n, 42, "func_ret_n"))
    checks.append(py_assert_eq(s, "hello", "func_ret_s"))
    return checks


def test_subscript_target_unpack() -> list[bool]:
    """左辺が Subscript の unpack"""
    checks: list[bool] = []
    a: list[int] = [0, 0, 0]
    a[0], a[1], a[2] = [10, 20, 30]
    checks.append(py_assert_eq(a[0], 10, "sub_a0"))
    checks.append(py_assert_eq(a[1], 20, "sub_a1"))
    checks.append(py_assert_eq(a[2], 30, "sub_a2"))
    return checks


def test_nested_unpack() -> list[bool]:
    """ネストした unpack"""
    checks: list[bool] = []
    a, (b, c) = 1, (2, 3)
    checks.append(py_assert_eq(a, 1, "nested_a"))
    checks.append(py_assert_eq(b, 2, "nested_b"))
    checks.append(py_assert_eq(c, 3, "nested_c"))
    return checks


def test_swap() -> list[bool]:
    """swap パターン"""
    checks: list[bool] = []
    x: int = 10
    y: int = 20
    x, y = y, x
    checks.append(py_assert_eq(x, 20, "swap_x"))
    checks.append(py_assert_eq(y, 10, "swap_y"))
    return checks


def run_tuple_unpack_variants() -> bool:
    checks: list[bool] = []
    checks.extend(test_basic_unpack())
    checks.extend(test_paren_unpack())
    checks.extend(test_bracket_unpack())
    checks.extend(test_list_rhs_unpack())
    checks.extend(test_comprehension_unpack())
    checks.extend(test_function_return_unpack())
    checks.extend(test_subscript_target_unpack())
    checks.extend(test_nested_unpack())
    checks.extend(test_swap())
    return py_assert_all(checks, "tuple_unpack_variants")


if __name__ == "__main__":
    print(run_tuple_unpack_variants())

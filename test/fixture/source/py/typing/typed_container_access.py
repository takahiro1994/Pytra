from pytra.utils.assertions import py_assert_all, py_assert_eq


def test_dict_items_tuple_unpack() -> list[bool]:
    """dict.items() の tuple unpack — for key, value in d.items()"""
    checks: list[bool] = []
    d: dict[str, int] = {"a": 1, "b": 2, "c": 3}
    total: int = 0
    keys: list[str] = []
    for key, value in d.items():
        total += value
        keys.append(key)
    checks.append(py_assert_eq(total, 6, "items_sum"))
    checks.append(py_assert_eq(len(keys), 3, "items_key_count"))
    return checks


def test_typed_dict_get() -> list[bool]:
    """typed dict.get() — 戻り値型が具体型"""
    checks: list[bool] = []
    d: dict[str, int] = {"x": 10, "y": 20}
    x: int = d.get("x", 0)
    z: int = d.get("z", -1)
    checks.append(py_assert_eq(x, 10, "get_existing"))
    checks.append(py_assert_eq(z, -1, "get_default"))

    sd: dict[str, str] = {"name": "alice"}
    name: str = sd.get("name", "")
    missing: str = sd.get("age", "unknown")
    checks.append(py_assert_eq(name, "alice", "get_str_existing"))
    checks.append(py_assert_eq(missing, "unknown", "get_str_default"))
    return checks


def test_typed_list_index() -> list[bool]:
    """typed list[T][i] — 要素型が具体型"""
    checks: list[bool] = []
    names: list[str] = ["alpha", "beta", "gamma"]
    first: str = names[0]
    last: str = names[2]
    checks.append(py_assert_eq(first, "alpha", "list_first"))
    checks.append(py_assert_eq(last, "gamma", "list_last"))

    nums: list[int] = [10, 20, 30, 40]
    checks.append(py_assert_eq(nums[1], 20, "list_int_index"))
    checks.append(py_assert_eq(nums[-1], 40, "list_negative_index"))
    return checks


def test_str_cast_on_known_str() -> list[bool]:
    """str() on known str value — 不要な unbox/cast を生成しないか"""
    checks: list[bool] = []
    d: dict[str, str] = {"key": "hello"}
    # str() on dict.get with str value type — should be no-op or simple
    val: str = str(d.get("key", ""))
    checks.append(py_assert_eq(val, "hello", "str_on_str_get"))

    # str() on int — legitimate cast
    n: int = 42
    s: str = str(n)
    checks.append(py_assert_eq(s, "42", "str_on_int"))

    # str() on dict[str, object].get — needs unbox
    od: dict[str, object] = {"name": "world"}
    name: str = str(od.get("name", ""))
    checks.append(py_assert_eq(name, "world", "str_on_object_get"))
    return checks


def test_dict_keys_values() -> list[bool]:
    """dict.keys() / dict.values() iteration"""
    checks: list[bool] = []
    d: dict[str, int] = {"a": 1, "b": 2}
    key_list: list[str] = []
    for k in d.keys():
        key_list.append(k)
    checks.append(py_assert_eq(len(key_list), 2, "keys_count"))

    val_sum: int = 0
    for v in d.values():
        val_sum += v
    checks.append(py_assert_eq(val_sum, 3, "values_sum"))
    return checks


def run_typed_container_access() -> bool:
    checks: list[bool] = []
    checks.extend(test_dict_items_tuple_unpack())
    checks.extend(test_typed_dict_get())
    checks.extend(test_typed_list_index())
    checks.extend(test_str_cast_on_known_str())
    checks.extend(test_dict_keys_values())
    return py_assert_all(checks, "typed_container_access")


if __name__ == "__main__":
    print(run_typed_container_access())

from pytra.utils.assertions import py_assert_all, py_assert_eq


def run_bytes_copy_semantics() -> bool:
    ba: bytearray = bytearray([1, 2, 3])
    b: bytes = bytes(ba)

    # Mutate the original bytearray AFTER copying to bytes
    ba[0] = 99
    ba.append(4)

    checks: list[bool] = []
    # bytes must be independent of the original bytearray
    checks.append(py_assert_eq(b[0], 1, "bytes copy independent"))
    checks.append(py_assert_eq(len(b), 3, "bytes copy len unchanged"))
    checks.append(py_assert_eq(ba[0], 99, "bytearray mutated"))
    checks.append(py_assert_eq(len(ba), 4, "bytearray grew"))

    # Also test bytes from bytes (should also be independent copy)
    b2: bytes = bytes(b)
    total: int = 0
    for v in b2:
        total += v
    checks.append(py_assert_eq(total, 6, "bytes from bytes sum"))
    return py_assert_all(checks, "bytes_copy_semantics")


if __name__ == "__main__":
    print(run_bytes_copy_semantics())

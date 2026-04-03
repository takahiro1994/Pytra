"""Pure-Python source-of-truth for containment helpers."""


def py_contains_dict_object[K, V](values: dict[K, V], key: K) -> bool:
    for cur in values:
        if cur == key:
            return True
    return False


def py_contains_list_object[T](values: list[T], key: T) -> bool:
    for cur in values:
        if cur == key:
            return True
    return False


def py_contains_set_object[T](values: set[T], key: T) -> bool:
    for cur in values:
        if cur == key:
            return True
    return False


def py_contains_str_object(values: str, key: str) -> bool:
    needle = key
    haystack = values
    n = len(haystack)
    m = len(needle)
    if m == 0:
        return True
    i = 0
    last = n - m
    while i <= last:
        j = 0
        ok = True
        while j < m:
            if haystack[i + j] != needle[j]:
                ok = False
                break
            j += 1
        if ok:
            return True
        i += 1
    return False

// AUTO-GENERATED FILE. DO NOT EDIT.
// source: src/pytra/utils/assertions.py
// generated-by: src/backends/cpp/cli.py

#ifndef PYTRA_GENERATED_UTILS_ASSERTIONS_H
#define PYTRA_GENERATED_UTILS_ASSERTIONS_H

#include "runtime/cpp/native/core/py_types.h"
#include "runtime/cpp/native/core/py_runtime.h"
#include "generated/built_in/io_ops.h"

namespace pytra::utils::assertions {

template <class T, class U>
static inline bool _eq_any(const T& actual, const U& expected) {
    return py_to_string(actual) == py_to_string(expected);
}

bool py_assert_true(bool cond, const str& label = "");

template <class T, class U>
static inline bool py_assert_eq(const T& actual, const U& expected, const str& label = "") {
    bool ok = _eq_any(actual, expected);
    if (ok)
        return true;
    if (label != "")
        py_print("[assert_eq] " + label + ": actual=" + str(py_to_string(actual)) + ", expected=" + str(py_to_string(expected)));
    else
        py_print("[assert_eq] actual=" + str(py_to_string(actual)) + ", expected=" + str(py_to_string(expected)));
    return false;
}

bool py_assert_all(const list<bool>& results, const str& label = "");

template <class Fn>
static inline bool py_assert_stdout(const list<str>& expected_lines, const Fn&) {
    // self_hosted parser / runtime 互換優先: stdout capture は未実装。
    return true;
}

}  // namespace pytra::utils::assertions

#endif  // PYTRA_GENERATED_UTILS_ASSERTIONS_H

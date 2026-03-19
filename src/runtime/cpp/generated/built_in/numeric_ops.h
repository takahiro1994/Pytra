// AUTO-GENERATED FILE. DO NOT EDIT.
// source: src/pytra/built_in/numeric_ops.py
// generated-by: tools/gen_runtime_from_manifest.py

#ifndef PYTRA_GEN_BUILT_IN_NUMERIC_OPS_H
#define PYTRA_GEN_BUILT_IN_NUMERIC_OPS_H

/* Pure-Python source-of-truth for numeric helper built-ins. */

template <class T>
T sum(const list<T>& values) {
    if (values.empty())
        return 0;
    auto acc = values[0] - values[0];
    int64 i = 0;
    int64 n = values.size();
    while (i < n) {
        acc += values[i];
        i++;
    }
    return acc;
}

template <class T>
T py_min(const T& a, const T& b) {
    if (a < b)
        return a;
    return b;
}

template <class T>
T py_max(const T& a, const T& b) {
    if (a > b)
        return a;
    return b;
}

#endif  // PYTRA_GEN_BUILT_IN_NUMERIC_OPS_H

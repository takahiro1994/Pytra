// AUTO-GENERATED FILE. DO NOT EDIT.
// source: src/pytra/built_in/predicates.py
// generated-by: src/backends/cpp/cli.py

#ifndef PYTRA_GENERATED_BUILT_IN_PREDICATES_H
#define PYTRA_GENERATED_BUILT_IN_PREDICATES_H

#include "runtime/cpp/native/core/py_types.h"

template <class T>
static inline bool py_any(const list<T>& values) {
    for (const auto& v : values) {
        if (static_cast<bool>(v)) return true;
    }
    return false;
}

template <class T>
static inline bool py_any(const rc<list<T>>& values) {
    if (!values) return false;
    return py_any(*values);
}

template <class T>
static inline bool py_all(const list<T>& values) {
    for (const auto& v : values) {
        if (!static_cast<bool>(v)) return false;
    }
    return true;
}

template <class T>
static inline bool py_all(const rc<list<T>>& values) {
    if (!values) return true;
    return py_all(*values);
}

#endif  // PYTRA_GENERATED_BUILT_IN_PREDICATES_H

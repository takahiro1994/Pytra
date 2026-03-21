#ifndef PYTRA_CORE_TAGGED_VALUE_H
#define PYTRA_CORE_TAGGED_VALUE_H

#include "core/py_types.h"

// PyBoxed<T, TID>: box any value type into an RcObject for legacy code.
// New code should use Object<T> + ControlBlock instead.
template <class T, pytra_type_id TID>
struct PyBoxed : RcObject {
    T value;
    PyBoxed() : value() {}
    explicit PyBoxed(const T& v) : value(v) {}
    pytra_type_id py_type_id() const noexcept override { return TID; }
};

// py_box: create an object from a POD value (legacy helper).
template <class T, pytra_type_id TID>
static inline object py_box(const T& v) {
    return object(make_object<PyBoxedValue<T>>(TID, v));
}

// py_unbox: extract a POD value from an object (legacy helper).
template <class T, pytra_type_id TID>
static inline const T& py_unbox(const object& v) {
    return static_cast<PyBoxedValue<T>*>(v.get())->value;
}

#endif  // PYTRA_CORE_TAGGED_VALUE_H

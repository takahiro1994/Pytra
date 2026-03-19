#ifndef PYTRA_CORE_TAGGED_VALUE_H
#define PYTRA_CORE_TAGGED_VALUE_H

#include "core/py_types.h"

// PyBoxed<T, TID>: box any value type into an RcObject for tagged union storage.
template <class T, pytra_type_id TID>
struct PyBoxed : RcObject {
    T value;
    PyBoxed() : value() {}
    explicit PyBoxed(const T& v) : value(v) {}
    pytra_type_id py_type_id() const noexcept override { return TID; }
};

// py_box: wrap a value into object (rc<RcObject>).
template <class T, pytra_type_id TID>
static inline object py_box(const T& v) {
    return object(new PyBoxed<T, TID>(v));
}

// py_unbox: extract the value from a boxed object.
template <class T, pytra_type_id TID>
static inline const T& py_unbox(const object& v) {
    return static_cast<PyBoxed<T, TID>*>(v.get())->value;
}

// PyTaggedValue: universal tagged union representation.
// All tagged unions use this single struct via typedef.
struct PyTaggedValue {
    pytra_type_id tag;
    object value;

    PyTaggedValue() : tag(PYTRA_TID_NONE), value() {}

    template <class T, pytra_type_id TID>
    static PyTaggedValue make(const T& v) {
        PyTaggedValue tv;
        tv.tag = TID;
        tv.value = py_box<T, TID>(v);
        return tv;
    }

    // Convenience constructors for common types.
    static PyTaggedValue from_none() {
        PyTaggedValue tv;
        tv.tag = PYTRA_TID_NONE;
        return tv;
    }
};

#endif  // PYTRA_CORE_TAGGED_VALUE_H

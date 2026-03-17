#ifndef PYTRA_BUILT_IN_PY_TYPES_H
#define PYTRA_BUILT_IN_PY_TYPES_H

#include <algorithm>
#include <any>
#include <cctype>
#include <deque>
#include <optional>
#include <stdexcept>
#include <string>
#include <tuple>
#include <type_traits>
#include <unordered_map>
#include <unordered_set>
#include <utility>
#include <vector>

#include "py_scalar_types.h"
#include "gc.h"
#include "io.h"

using RcObject = pytra::gc::RcObject;

template <class T>
using rc = pytra::gc::RcHandle<T>;

using object = rc<RcObject>;

template <class T, class... Args>
static inline rc<T> rc_new(Args&&... args) {
    return rc<T>::adopt(pytra::gc::rc_new<T>(::std::forward<Args>(args)...));
}

class str;
template <class T> class list;
template <class K, class V> class dict;

#include "str.h"
#include "list.h"
#include "dict.h"
#include "set.h"

template <class T>
struct py_is_rc_list_handle : ::std::false_type {};

template <class T>
struct py_is_rc_list_handle<rc<list<T>>> : ::std::true_type {
    using item_type = T;
};

template <class T>
static inline rc<list<T>> rc_list_new() {
    return rc<list<T>>::adopt(pytra::gc::rc_new<list<T>>());
}

template <class T>
static inline rc<list<T>> rc_list_from_value(list<T> values) {
    return rc<list<T>>::adopt(pytra::gc::rc_new<list<T>>(::std::move(values)));
}

template <class T>
static inline list<T>& rc_list_ref(rc<list<T>>& values) {
    if (!values) {
        throw ::std::runtime_error("rc_list_ref: null list handle");
    }
    return *values;
}

template <class T>
static inline const list<T>& rc_list_ref(const rc<list<T>>& values) {
    if (!values) {
        throw ::std::runtime_error("rc_list_ref: null list handle");
    }
    return *values;
}

template <class T>
static inline list<T> rc_list_copy_value(const rc<list<T>>& values) {
    if (!values) {
        return list<T>{};
    }
    return *values;
}

#endif  // PYTRA_BUILT_IN_PY_TYPES_H

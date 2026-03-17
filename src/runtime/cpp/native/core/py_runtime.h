#ifndef PYTRA_BUILT_IN_PY_RUNTIME_H
#define PYTRA_BUILT_IN_PY_RUNTIME_H

#include <algorithm>
#include <cmath>
#include <cstdint>
#include <optional>
#include <sstream>
#include <stdexcept>
#include <string>
#include <type_traits>
#include <tuple>
#include <unordered_map>
#include <unordered_set>
#include <utility>
#include <vector>

#include "py_types.h"
#include "exceptions.h"
#include "io.h"
// `str` method delegates still live here, so string helper declarations remain a direct dependency.
#include "runtime/cpp/generated/built_in/string_ops.h"

// type_id は target 非依存で stable な型判定キーとして扱う。
// 予約領域（0-999）は runtime 組み込み型に割り当てる。
static constexpr uint32 PYTRA_TID_NONE = 0;
static constexpr uint32 PYTRA_TID_BOOL = 1;
static constexpr uint32 PYTRA_TID_INT = 2;
static constexpr uint32 PYTRA_TID_FLOAT = 3;
static constexpr uint32 PYTRA_TID_STR = 4;
static constexpr uint32 PYTRA_TID_LIST = 5;
static constexpr uint32 PYTRA_TID_DICT = 6;
static constexpr uint32 PYTRA_TID_SET = 7;
static constexpr uint32 PYTRA_TID_OBJECT = 8;
static constexpr uint32 PYTRA_TID_USER_BASE = 1000;

inline list<str> str::split(const str& sep, int64 maxsplit) const {
    return py_split(*this, sep, maxsplit);
}

inline list<str> str::split(const str& sep) const {
    return split(sep, -1);
}

inline list<str> str::splitlines() const {
    return py_splitlines(*this);
}

inline int64 str::count(const str& needle) const {
    return py_count(*this, needle);
}

inline str str::join(const list<str>& parts) const {
    return py_join(*this, parts);
}

template <class T>
static inline int64 py_len(const rc<list<T>>& v) {
    if (!v) return 0;
    return static_cast<int64>(v->size());
}

// Python 組み込み相当の基本ユーティリティ（len / 文字列化）。
template <class T>
static inline int64 py_len(const T& v) {
    return static_cast<int64>(v.size());
}

template <class T>
static inline int64 py_len(const ::std::optional<T>& v) {
    if (!v.has_value()) return 0;
    return py_len(*v);
}

template <::std::size_t N>
static inline int64 py_len(const char (&)[N]) {
    return N > 0 ? static_cast<int64>(N - 1) : 0;
}

template <class T>
static inline ::std::string py_to_string(const T& v) {
    ::std::ostringstream oss;
    oss << v;
    return oss.str();
}

static inline ::std::string py_to_string(const ::std::string& v) {
    return v;
}

static inline ::std::string py_to_string(const ::std::exception& v) {
    return ::std::string(v.what());
}

static inline ::std::string py_to_string(uint8 v) {
    return ::std::to_string(static_cast<int>(v));
}

static inline ::std::string py_to_string(int8 v) {
    return ::std::to_string(static_cast<int>(v));
}

static inline ::std::string py_to_string(const char* v) {
    return ::std::string(v);
}

template <class T>
static inline ::std::string py_to_string(const ::std::optional<T>& v) {
    if (!v.has_value()) return "None";
    return py_to_string(*v);
}

template <class T>
static inline T py_to(const T& v);

static inline int64 py_to_int64(const str& v) {
    return static_cast<int64>(::std::stoll(v));
}

template <class T, ::std::enable_if_t<::std::is_arithmetic_v<T>, int> = 0>
static inline int64 py_to_int64(T v) {
    return py_to<int64>(v);
}

static inline float64 py_to_float64(const str& v) {
    return static_cast<float64>(::std::stod(v.std()));
}

template <class T, ::std::enable_if_t<::std::is_arithmetic_v<T>, int> = 0>
static inline float64 py_to_float64(T v) {
    return py_to<float64>(v);
}

template <class T>
static inline bool py_to_bool(const rc<list<T>>& v) {
    return v && !v->empty();
}

static inline bool py_to_bool(bool v) {
    return py_to<bool>(v);
}

template <class T>
struct py_is_list_type : ::std::false_type {};

template <class T>
struct py_is_list_type<list<T>> : ::std::true_type {
    using item_type = T;
};

template <class T>
struct py_is_list_type<rc<list<T>>> : ::std::true_type {
    using item_type = T;
};

template <class T>
static inline T py_to(const T& v) {
    return v;
}

template <class T>
static inline list<T> py_list_slice_copy(const list<T>& values, int64 lo, int64 up) {
    const int64 n = static_cast<int64>(values.size());
    if (lo < 0) lo += n;
    if (up < 0) up += n;
    lo = ::std::max<int64>(0, ::std::min<int64>(lo, n));
    up = ::std::max<int64>(0, ::std::min<int64>(up, n));
    if (up < lo) up = lo;
    return list<T>(values.begin() + lo, values.begin() + up);
}

template <class T>
static inline int64 py_list_normalize_index_or_raise(const list<T>& values, int64 idx, const char* label) {
    int64 pos = idx;
    const int64 n = static_cast<int64>(values.size());
    if (pos < 0) pos += n;
    if (pos < 0 || pos >= n) {
        throw ::std::out_of_range(label);
    }
    return pos;
}

template <class T>
static inline typename list<T>::reference py_list_at_ref(list<T>& values, int64 idx) {
    const int64 pos = py_list_normalize_index_or_raise(values, idx, "list index out of range");
    return values[static_cast<::std::size_t>(pos)];
}

template <class T>
static inline typename list<T>::const_reference py_list_at_ref(const list<T>& values, int64 idx) {
    const int64 pos = py_list_normalize_index_or_raise(values, idx, "list index out of range");
    return values[static_cast<::std::size_t>(pos)];
}

template <class T>
struct py_is_cstr_like : ::std::bool_constant<
    ::std::is_pointer_v<::std::decay_t<T>>
    && ::std::is_same_v<
        ::std::remove_cv_t<::std::remove_pointer_t<::std::decay_t<T>>>,
        char>> {};

template <class T>
static inline T py_coerce_cstr_typed_value(const char* value) {
    if constexpr (::std::is_same_v<T, str>) {
        return str(value);
    } else if constexpr (::std::is_same_v<T, bool>) {
        return str(value).size() != 0;
    } else if constexpr (::std::is_integral_v<T> && !::std::is_same_v<T, bool>) {
        return static_cast<T>(py_to_int64(str(value)));
    } else if constexpr (::std::is_floating_point_v<T>) {
        return static_cast<T>(py_to_float64(str(value)));
    } else if constexpr (::std::is_convertible_v<const char*, T>) {
        return static_cast<T>(value);
    } else if constexpr (::std::is_constructible_v<T, const char*>) {
        return T(value);
    } else if constexpr (::std::is_convertible_v<str, T>) {
        return static_cast<T>(str(value));
    } else if constexpr (::std::is_constructible_v<T, str>) {
        return T(str(value));
    } else {
        static_assert(!::std::is_same_v<T, T>, "py_coerce_cstr_typed_value<T>: unsupported target type");
    }
}

template <class T, class U>
static inline void py_list_append_mut(list<T>& values, const U& item) {
    if constexpr (py_is_cstr_like<U>::value) {
        values.append(py_coerce_cstr_typed_value<T>(item));
    } else if constexpr (::std::is_same_v<T, U>) {
        values.append(item);
    } else if constexpr (::std::is_convertible_v<U, T>) {
        values.append(static_cast<T>(item));
    } else {
        values.append(T(item));
    }
}

template <class T, class I, class U>
static inline void py_list_set_at_mut(list<T>& values, I idx, const U& item) {
    int64 pos = py_to<int64>(idx);
    pos = py_list_normalize_index_or_raise(values, pos, "list index out of range");
    if constexpr (py_is_cstr_like<U>::value) {
        values[static_cast<::std::size_t>(pos)] = py_coerce_cstr_typed_value<T>(item);
    } else if constexpr (::std::is_same_v<T, U>) {
        values[static_cast<::std::size_t>(pos)] = item;
    } else if constexpr (::std::is_convertible_v<U, T>) {
        values[static_cast<::std::size_t>(pos)] = static_cast<T>(item);
    } else {
        values[static_cast<::std::size_t>(pos)] = T(item);
    }
}

template <class T, class U>
static inline void py_list_extend_mut(list<T>& values, const U& items) {
    values.extend(items);
}

template <class T>
static inline T py_list_pop_mut(list<T>& values) {
    return values.pop();
}

template <class T>
static inline T py_list_pop_mut(list<T>& values, int64 idx) {
    return values.pop(idx);
}

template <class T>
static inline void py_list_clear_mut(list<T>& values) {
    values.clear();
}

template <class T>
static inline void py_list_reverse_mut(list<T>& values) {
    ::std::reverse(values.begin(), values.end());
}

template <class T>
static inline void py_list_sort_mut(list<T>& values) {
    ::std::sort(values.begin(), values.end());
}

template <class T>
static inline list<T> py_slice(const list<T>& v, int64 lo, int64 up) {
    return py_list_slice_copy(v, lo, up);
}

template <class T>
static inline list<T> py_slice(const rc<list<T>>& v, int64 lo, int64 up) {
    return py_list_slice_copy(rc_list_ref(v), lo, up);
}

static inline str py_slice(const str& v, int64 lo, int64 up) {
    const int64 n = static_cast<int64>(v.size());
    if (lo < 0) lo += n;
    if (up < 0) up += n;
    lo = ::std::max<int64>(0, ::std::min<int64>(lo, n));
    up = ::std::max<int64>(0, ::std::min<int64>(up, n));
    if (up < lo) up = lo;
    return v.substr(static_cast<::std::size_t>(lo), static_cast<::std::size_t>(up - lo));
}

template <class T>
static inline typename list<T>::const_reference py_at(const list<T>& v, int64 idx) {
    return py_list_at_ref(v, idx);
}

template <class T>
static inline typename list<T>::reference py_at(rc<list<T>>& v, int64 idx) {
    return py_list_at_ref(rc_list_ref(v), idx);
}

template <class T>
static inline typename list<T>::const_reference py_at(const rc<list<T>>& v, int64 idx) {
    return py_list_at_ref(rc_list_ref(v), idx);
}

template <class K, class V, class Q>
static inline V& py_at(dict<K, V>& d, const Q& key) {
    const K k = [&]() -> K {
        if constexpr (py_is_cstr_like<Q>::value) {
            return py_coerce_cstr_typed_value<K>(key);
        } else if constexpr (::std::is_same_v<K, Q>) {
            return key;
        } else if constexpr (::std::is_convertible_v<Q, K>) {
            return static_cast<K>(key);
        } else {
            return K(key);
        }
    }();
    auto it = d.find(k);
    if (it == d.end()) {
        throw ::std::out_of_range("dict key not found");
    }
    return it->second;
}

template <class K, class V, class Q>
static inline const V& py_at(const dict<K, V>& d, const Q& key) {
    const K k = [&]() -> K {
        if constexpr (py_is_cstr_like<Q>::value) {
            return py_coerce_cstr_typed_value<K>(key);
        } else if constexpr (::std::is_same_v<K, Q>) {
            return key;
        } else if constexpr (::std::is_convertible_v<Q, K>) {
            return static_cast<K>(key);
        } else {
            return K(key);
        }
    }();
    auto it = d.find(k);
    if (it == d.end()) {
        throw ::std::out_of_range("dict key not found");
    }
    return it->second;
}

template <class T>
static inline int64 py_index(const list<T>& v, const T& item) {
    return v.index(item);
}

template <class Seq>
static inline decltype(auto) py_at_bounds(Seq& v, int64 idx) {
    const int64 n = py_len(v);
    if (idx < 0 || idx >= n) throw ::std::out_of_range("index out of range");
    return v[static_cast<::std::size_t>(idx)];
}

template <class Seq>
static inline decltype(auto) py_at_bounds(const Seq& v, int64 idx) {
    const int64 n = py_len(v);
    if (idx < 0 || idx >= n) throw ::std::out_of_range("index out of range");
    return v[static_cast<::std::size_t>(idx)];
}

template <class Seq>
static inline decltype(auto) py_at_bounds_debug(Seq& v, int64 idx) {
#ifndef NDEBUG
    return py_at_bounds(v, idx);
#else
    return v[static_cast<::std::size_t>(idx)];
#endif
}

template <class Seq>
static inline decltype(auto) py_at_bounds_debug(const Seq& v, int64 idx) {
#ifndef NDEBUG
    return py_at_bounds(v, idx);
#else
    return v[static_cast<::std::size_t>(idx)];
#endif
}

// Python の型判定（isinstance 的な分岐）で使う述語群。
template <class T>
static inline bool py_is_none(const ::std::optional<T>& v) {
    return !v.has_value();
}

template <class T>
static inline bool py_is_none(const T&) {
    return false;
}

static inline bool py_is_none(const object& v) {
    return !static_cast<bool>(v);
}

template <class T> static inline bool py_is_dict(const T&) { return false; }
template <class T> static inline bool py_is_list(const T&) { return false; }
template <class T> static inline bool py_is_set(const T&) { return false; }
template <class T> static inline bool py_is_str(const T&) { return false; }
template <class T> static inline bool py_is_bool(const T&) { return false; }

template <class K, class V> static inline bool py_is_dict(const dict<K, V>&) { return true; }
template <class U> static inline bool py_is_list(const list<U>&) { return true; }
template <class U> static inline bool py_is_list(const rc<list<U>>&) { return true; }
template <class U> static inline bool py_is_set(const set<U>&) { return true; }
static inline bool py_is_str(const str&) { return true; }
template <class T> static inline bool py_is_int(const T&) { return ::std::is_integral_v<T> && !::std::is_same_v<T, bool>; }
template <class T> static inline bool py_is_float(const T&) { return ::std::is_floating_point_v<T>; }
static inline bool py_is_bool(const bool&) { return true; }

// P0-contract-shrink label: shared_type_id_contract seam.
// type_id 判定ロジックは generated built_in 層（py_tid_*）を正本とする。
#include "runtime/cpp/generated/built_in/type_id.h"

static inline dict<uint32, uint32>& py_runtime_user_type_base_registry() {
    static dict<uint32, uint32> user_type_base{};
    return user_type_base;
}

static inline uint32& py_runtime_next_user_type_id() {
    static uint32 next_user_type_id = 1000;
    return next_user_type_id;
}

static inline uint32& py_runtime_synced_user_type_count() {
    static uint32 synced_user_type_count = 0;
    return synced_user_type_count;
}

static inline void py_sync_generated_user_type_registry() {
    auto& user_type_base = py_runtime_user_type_base_registry();
    if (user_type_base.empty()) {
        return;
    }
    auto& synced_user_type_count = py_runtime_synced_user_type_count();
    uint32 next_user_type_id = py_runtime_next_user_type_id();
    uint32 last_registered_tid = next_user_type_id - 1;
    bool needs_sync = synced_user_type_count != user_type_base.size();
    if (!needs_sync) {
        auto last_it = user_type_base.find(last_registered_tid);
        if (last_it != user_type_base.end()) {
            needs_sync = _TYPE_BASE.find(static_cast<int64>(last_registered_tid)) == _TYPE_BASE.end();
        }
    }
    if (!needs_sync) {
        return;
    }
    for (uint32 tid = 1000; tid < next_user_type_id; ++tid) {
        auto it = user_type_base.find(tid);
        if (it == user_type_base.end()) {
            continue;
        }
        py_tid_register_known_class_type(static_cast<int64>(tid), static_cast<int64>(it->second));
    }
    synced_user_type_count = static_cast<uint32>(user_type_base.size());
}

static inline uint32 py_register_class_type(uint32 base_type_id = PYTRA_TID_OBJECT) {
    // NOTE:
    // Avoid cross-TU static initialization order issues by keeping user type
    // registry in function-local statics (initialized on first use).
    auto& user_type_base = py_runtime_user_type_base_registry();
    uint32 tid = py_runtime_next_user_type_id();
    while (user_type_base.find(tid) != user_type_base.end()) {
        ++tid;
    }
    py_runtime_next_user_type_id() = tid + 1;
    user_type_base[tid] = base_type_id;
    return tid;
}

// Generated user classes share this exact type-id boilerplate.
// Keep it in runtime so backend output stays compact and consistent.
#define PYTRA_DECLARE_CLASS_TYPE(BASE_TYPE_ID_EXPR)                                                     \
    inline static uint32 PYTRA_TYPE_ID = py_register_class_type((BASE_TYPE_ID_EXPR));                   \
    uint32 py_type_id() const noexcept override {                                                        \
        return PYTRA_TYPE_ID;                                                                            \
}

static inline bool py_runtime_type_id_is_subtype(uint32 actual_type_id, uint32 expected_type_id) {
    py_sync_generated_user_type_registry();
    return py_tid_is_subtype(static_cast<int64>(actual_type_id), static_cast<int64>(expected_type_id));
}

static inline bool py_runtime_type_id_issubclass(uint32 actual_type_id, uint32 expected_type_id) {
    py_sync_generated_user_type_registry();
    return py_tid_issubclass(static_cast<int64>(actual_type_id), static_cast<int64>(expected_type_id));
}

static inline uint32 py_runtime_object_type_id(const object& v) {
    if (!v) {
        return PYTRA_TID_NONE;
    }
    uint32 out = v->py_type_id();
    if (out == 0) {
        return PYTRA_TID_OBJECT;
    }
    return out;
}

static inline bool py_runtime_object_isinstance(const object& value, uint32 expected_type_id) {
    if (!value) {
        return expected_type_id == PYTRA_TID_NONE;
    }
    py_sync_generated_user_type_registry();
    return py_tid_isinstance(value, static_cast<int64>(expected_type_id));
}

template <class T>
static inline uint32 _py_static_type_id_for() {
    if constexpr (::std::is_same_v<T, bool>) return PYTRA_TID_BOOL;
    else if constexpr (::std::is_integral_v<T>) return PYTRA_TID_INT;
    else if constexpr (::std::is_floating_point_v<T>) return PYTRA_TID_FLOAT;
    else if constexpr (::std::is_same_v<T, str>) return PYTRA_TID_STR;
    else return PYTRA_TID_OBJECT;
}

template <class T>
static inline uint32 py_runtime_value_type_id(const T& value) {
    (void)value;
    return _py_static_type_id_for<T>();
}

template <class K, class V>
static inline uint32 py_runtime_value_type_id(const dict<K, V>&) { return PYTRA_TID_DICT; }

template <class T>
static inline uint32 py_runtime_value_type_id(const list<T>&) { return PYTRA_TID_LIST; }

template <class T>
static inline uint32 py_runtime_value_type_id(const set<T>&) { return PYTRA_TID_SET; }

template <class T>
static inline uint32 py_runtime_value_type_id(const rc<T>& value) {
    if (!value) return PYTRA_TID_NONE;
    uint32 out = value->py_type_id();
    return out == 0 ? PYTRA_TID_OBJECT : out;
}

template <class T>
static inline bool py_runtime_value_isinstance(const T& value, uint32 expected_type_id) {
    return py_runtime_type_id_is_subtype(py_runtime_value_type_id(value), expected_type_id);
}

// Specialization for user-defined ref classes that inherit RcObject.
// Uses the virtual py_type_id() on the RcObject base.
template <class T, ::std::enable_if_t<::std::is_base_of_v<RcObject, T>, int> = 0>
static inline bool py_runtime_value_isinstance(const rc<T>& value, uint32 expected_type_id) {
    if (!value) return expected_type_id == PYTRA_TID_NONE;
    return py_runtime_type_id_is_subtype(value->py_type_id(), expected_type_id);
}

template <class T, ::std::enable_if_t<::std::is_arithmetic_v<T>, int> = 0>
static inline auto operator-(const rc<T>& v) -> decltype(v->__neg__()) {
    return v->__neg__();
}

// `/` / `//` / `%` の Python 互換セマンティクス（とくに負数時の扱い）を提供する。
template <class A, class B>
static inline float64 py_div(A lhs, B rhs) {
    return py_to_float64(lhs) / py_to_float64(rhs);
}

template <class A, class B>
static inline auto py_floordiv(A lhs, B rhs) {
    using R = ::std::common_type_t<A, B>;
    if constexpr (::std::is_integral_v<A> && ::std::is_integral_v<B>) {
        if (rhs == 0) throw ::std::runtime_error("division by zero");
        R q = static_cast<R>(lhs / rhs);
        R r = static_cast<R>(lhs % rhs);
        if (r != 0 && ((r > 0) != (rhs > 0))) q -= 1;
        return q;
    } else {
        return ::std::floor(static_cast<float64>(lhs) / static_cast<float64>(rhs));
    }
}

template <class A, class B>
static inline auto py_mod(A lhs, B rhs) {
    using R = ::std::common_type_t<A, B>;
    if constexpr (::std::is_integral_v<A> && ::std::is_integral_v<B>) {
        if (rhs == 0) throw ::std::runtime_error("integer modulo by zero");
        R r = static_cast<R>(lhs % rhs);
        if (r != 0 && ((r > 0) != (rhs > 0))) r += static_cast<R>(rhs);
        return r;
    } else {
        float64 lf = static_cast<float64>(lhs);
        float64 rf = static_cast<float64>(rhs);
        if (rf == 0.0) throw ::std::runtime_error("float modulo");
        float64 r = ::std::fmod(lf, rf);
        if (r != 0.0 && ((r > 0.0) != (rf > 0.0))) r += rf;
        return r;
    }
}

#endif  // PYTRA_BUILT_IN_PY_RUNTIME_H

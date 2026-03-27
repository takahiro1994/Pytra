#ifndef PYTRA_BUILT_IN_STRING_OPS_FWD_H
#define PYTRA_BUILT_IN_STRING_OPS_FWD_H

// Forward declarations for generated string_ops functions.
// The full implementations are generated from runtime/east/built_in/string_ops.east
// by the emit pipeline. This header provides minimal declarations so that
// native headers (str_methods.h) can reference them without depending on
// generated files being present in the source tree.

#include "core/py_types.h"

Object<list<str>> py_split(const str& s, const str& sep, int64 maxsplit = -1);
Object<list<str>> py_splitlines(const str& s);
int64 py_count(const str& s, const str& needle);
str py_join(const str& sep, const Object<list<str>>& parts);
str py_replace(const str& s, const str& oldv, const str& newv);
str py_replace_n(const str& s, const str& oldv, const str& newv, int count);
bool py_startswith(const str& s, const str& prefix);
bool py_endswith(const str& s, const str& suffix);
int64 py_find(const str& s, const str& needle);
int64 py_rfind(const str& s, const str& needle);
int64 py_find_window(const str& s, const str& needle, int64 start, int64 end);
int64 py_rfind_window(const str& s, const str& needle, int64 start, int64 end);
str py_strip(const str& s);
str py_lstrip(const str& s);
str py_rstrip(const str& s);
str py_strip_chars(const str& s, const str& chars);
str py_lstrip_chars(const str& s, const str& chars);
str py_rstrip_chars(const str& s, const str& chars);
bool py_isdigit(const str& s);
bool py_isalpha(const str& s);
str py_zfill(const str& s, int64 width);
str py_lower(const str& s);
str py_upper(const str& s);

#endif  // PYTRA_BUILT_IN_STRING_OPS_FWD_H

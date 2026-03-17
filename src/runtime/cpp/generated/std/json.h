// AUTO-GENERATED FILE. DO NOT EDIT.
// source: src/pytra/std/json.py
// generated-by: src/backends/cpp/cli.py

#ifndef PYTRA_GENERATED_STD_JSON_H
#define PYTRA_GENERATED_STD_JSON_H

#include "runtime/cpp/native/core/py_runtime.h"

#include <tuple>
#include <optional>

namespace pytra::std::json {

struct _JsonVal;
struct JsonObj;
struct JsonArr;
struct JsonValue;
struct _JsonParser;

extern str _EMPTY;
extern str _COMMA_NL;
extern str _HEX_DIGITS;
extern int64 _JV_NULL;
extern int64 _JV_BOOL;
extern int64 _JV_INT;
extern int64 _JV_FLOAT;
extern int64 _JV_STR;
extern int64 _JV_ARR;
extern int64 _JV_OBJ;

    struct _JsonVal {
        int64 tag;
        bool bool_val;
        int64 int_val;
        float64 float_val;
        str str_val;
        rc<list<_JsonVal>> arr_val;
        dict<str, _JsonVal> obj_val;
        
        _JsonVal(int64 tag, bool bool_val, int64 int_val, float64 float_val, const str& str_val, const rc<list<_JsonVal>>& arr_val, const dict<str, _JsonVal>& obj_val);
    };

    struct JsonObj {
        dict<str, _JsonVal> raw;
        
        JsonObj(const dict<str, _JsonVal>& raw);
        ::std::optional<JsonValue> get(const str& key) const;
        ::std::optional<JsonObj> get_obj(const str& key) const;
        ::std::optional<JsonArr> get_arr(const str& key) const;
        ::std::optional<str> get_str(const str& key) const;
        ::std::optional<int64> get_int(const str& key) const;
        ::std::optional<float64> get_float(const str& key) const;
        ::std::optional<bool> get_bool(const str& key) const;
    };

    struct JsonArr {
        rc<list<_JsonVal>> raw;
        
        JsonArr(const rc<list<_JsonVal>>& raw);
        ::std::optional<JsonValue> get(int64 index) const;
        ::std::optional<JsonObj> get_obj(int64 index) const;
        ::std::optional<JsonArr> get_arr(int64 index) const;
        ::std::optional<str> get_str(int64 index) const;
        ::std::optional<int64> get_int(int64 index) const;
        ::std::optional<float64> get_float(int64 index) const;
        ::std::optional<bool> get_bool(int64 index) const;
    };

    struct JsonValue {
        _JsonVal raw;
        
        JsonValue(const _JsonVal& raw);
        ::std::optional<JsonObj> as_obj() const;
        ::std::optional<JsonArr> as_arr() const;
        ::std::optional<str> as_str() const;
        ::std::optional<int64> as_int() const;
        ::std::optional<float64> as_float() const;
        ::std::optional<bool> as_bool() const;
    };

    struct _JsonParser {
        str text;
        int64 n;
        int64 i;
        
        _JsonParser(const str& text);
        _JsonVal parse();
        void _skip_ws();
        _JsonVal _parse_value();
        dict<str, _JsonVal> _parse_object();
        rc<list<_JsonVal>> _parse_array();
        str _parse_string();
        _JsonVal _parse_number();
    };


bool _is_ws(const str& ch);
bool _is_digit(const str& ch);
int64 _hex_value(const str& ch);
int64 _int_from_hex4(const str& hx);
str _hex4(int64 code);
int64 _json_indent_value(const ::std::optional<int64>& indent);
_JsonVal _jv_null();
_JsonVal _jv_bool(bool v);
_JsonVal _jv_int(int64 v);
_JsonVal _jv_float(float64 v);
_JsonVal _jv_str(const str& v);
_JsonVal _jv_arr(const rc<list<_JsonVal>>& v);
_JsonVal _jv_obj(const dict<str, _JsonVal>& v);
_JsonVal _jv_obj_require(const dict<str, _JsonVal>& raw, const str& key);
JsonValue loads(const str& text);
::std::optional<JsonObj> loads_obj(const str& text);
::std::optional<JsonArr> loads_arr(const str& text);
str _join_strs(const rc<list<str>>& parts, const str& sep);
str _escape_str(const str& s, bool ensure_ascii);
str _dump_json_list(const rc<list<_JsonVal>>& values, bool ensure_ascii, const ::std::optional<int64>& indent, const str& item_sep, const str& key_sep, int64 level);
str _dump_json_dict(const dict<str, _JsonVal>& values, bool ensure_ascii, const ::std::optional<int64>& indent, const str& item_sep, const str& key_sep, int64 level);
str _dump_json_value(const _JsonVal& v, bool ensure_ascii, const ::std::optional<int64>& indent, const str& item_sep, const str& key_sep, int64 level);
str dumps(const _JsonVal& obj, bool ensure_ascii = true, const ::std::optional<int64>& indent = ::std::nullopt, const ::std::optional<::std::tuple<str, str>>& separators = ::std::nullopt);
str dumps_jv(const _JsonVal& jv, bool ensure_ascii = true, const ::std::optional<int64>& indent = ::std::nullopt, const ::std::optional<::std::tuple<str, str>>& separators = ::std::nullopt);

}  // namespace pytra::std::json

#endif  // PYTRA_GENERATED_STD_JSON_H

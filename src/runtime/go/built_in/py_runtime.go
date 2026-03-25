// py_runtime.go: Python built-in function equivalents.
// Only contains Python built-in functions. pytra.std.* and pytra.utils.* are
// provided by native files (std/) or pipeline-generated code (utils/).
// See docs/ja/spec/spec-emitter-guide.md §6.
package main

import (
	"fmt"
	"strconv"
	"strings"
)

func __pytra_print(args ...interface{}) {
	parts := make([]string, len(args))
	for i, a := range args { parts[i] = fmt.Sprint(a) }
	fmt.Println(strings.Join(parts, " "))
}

func __pytra_str(v interface{}) string { return fmt.Sprint(v) }

func __pytra_len(v interface{}) int64 {
	switch t := v.(type) {
	case string: return int64(len(t))
	case []int64: return int64(len(t))
	case []float64: return int64(len(t))
	case []string: return int64(len(t))
	case []byte: return int64(len(t))
	case []interface{}: return int64(len(t))
	default: return 0
	}
}

func __pytra_abs(v int64) int64 { if v < 0 { return -v }; return v }
func __pytra_abs_float(v float64) float64 { if v < 0 { return -v }; return v }
func __pytra_min_int(a, b int64) int64 { if a < b { return a }; return b }
func __pytra_max_int(a, b int64) int64 { if a > b { return a }; return b }
func __pytra_min_float(a, b float64) float64 { if a < b { return a }; return b }
func __pytra_max_float(a, b float64) float64 { if a > b { return a }; return b }

func __pytra_floordiv(a, b int64) int64 {
	q := a / b
	if (a^b) < 0 && q*b != a { q -= 1 }
	return q
}

func __pytra_contains(haystack interface{}, needle interface{}) bool {
	switch h := haystack.(type) {
	case string:
		n, ok := needle.(string); if ok { return strings.Contains(h, n) }
	case []int64:
		n, ok := needle.(int64); if ok { for _, v := range h { if v == n { return true } } }
	case map[string]int64:
		n, ok := needle.(string); if ok { _, exists := h[n]; return exists }
	}
	return false
}

func __pytra_ternary_int(cond bool, a, b int64) int64 { if cond { return a }; return b }
func __pytra_ternary_float(cond bool, a, b float64) float64 { if cond { return a }; return b }
func __pytra_ternary_str(cond bool, a, b string) string { if cond { return a }; return b }
func __pytra_append_byte(s []byte, v int64) []byte { return append(s, byte(v)) }

func __pytra_list_pop(s *[]interface{}, args ...int64) interface{} {
	sl := *s; n := len(sl); idx := n - 1
	if len(args) > 0 { idx = int(args[0]); if idx < 0 { idx += n } }
	val := sl[idx]; *s = append(sl[:idx], sl[idx+1:]...); return val
}

func __pytra_repeat_int64(val, count int64) []int64 {
	s := make([]int64, count)
	for i := int64(0); i < count; i++ { s[i] = val }
	return s
}

// String methods
func __pytra_isdigit(v interface{}) bool {
	switch t := v.(type) {
	case byte: return t >= '0' && t <= '9'
	case string:
		if len(t) == 0 { return false }
		for _, c := range t { if c < '0' || c > '9' { return false } }
		return true
	}
	return false
}
func __pytra_isalpha(v interface{}) bool {
	switch t := v.(type) {
	case byte: return (t >= 'a' && t <= 'z') || (t >= 'A' && t <= 'Z')
	case string:
		if len(t) == 0 { return false }
		for _, c := range t { if !((c >= 'a' && c <= 'z') || (c >= 'A' && c <= 'Z')) { return false } }
		return true
	}
	return false
}
func __pytra_strip(s string) string { return strings.TrimSpace(s) }
func __pytra_join(sep string, items []string) string { return strings.Join(items, sep) }
func __pytra_replace(s, old, new_ string) string { return strings.ReplaceAll(s, old, new_) }
func __pytra_split(s, sep string) []string { return strings.Split(s, sep) }
func __pytra_startswith(s, prefix string) bool { return strings.HasPrefix(s, prefix) }
func __pytra_endswith(s, suffix string) bool { return strings.HasSuffix(s, suffix) }
func __pytra_upper(s string) string { return strings.ToUpper(s) }
func __pytra_lower(s string) string { return strings.ToLower(s) }
func __pytra_find(s, sub string) int64 { return int64(strings.Index(s, sub)) }

// Dict
func __pytra_dict_get(m map[string]int64, key string, def_ int64) int64 {
	if v, ok := m[key]; ok { return v }; return def_
}

// Type conversions
func __pytra_byte_eq(b byte, s string) bool { return len(s) == 1 && b == s[0] }
func __pytra_byte_to_string(b byte) string { return string([]byte{b}) }
func __pytra_str_to_int64(s string) int64 { v, _ := strconv.ParseInt(s, 10, 64); return v }
func __pytra_str_to_float64(s string) float64 { v, _ := strconv.ParseFloat(s, 64); return v }

func _toF64(v interface{}) float64 {
	switch t := v.(type) {
	case float64: return t
	case int64: return float64(t)
	case int: return float64(t)
	case float32: return float64(t)
	default: return 0
	}
}
func __pytra_to_int64(v interface{}) int64 {
	switch t := v.(type) {
	case int64: return t; case int: return int64(t); case float64: return int64(t); default: return 0
	}
}
func __pytra_to_float64(v interface{}) float64 { return _toF64(v) }
func __pytra_int64(v interface{}) int64 {
	switch t := v.(type) {
	case int: return int64(t); case int64: return t; case float64: return int64(t)
	case string: r, _ := strconv.ParseInt(t, 10, 64); return r
	}; return 0
}

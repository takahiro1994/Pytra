// pytra_runtime.go: toolchain2 Go emitter 用ランタイム。
//
// toolchain2/emit/go/ が生成するコードが呼び出す関数を提供する。
// 関数名は EAST3 の import 名 / runtime_call 名に一致させる。
//
// source: src/runtime/go/toolchain2/pytra_runtime.go

package main

import (
	"fmt"
	"os"
	"path/filepath"
	"strings"
	"time"
)

// ---------------------------------------------------------------------------
// print / str
// ---------------------------------------------------------------------------

// __pytra_print emulates Python's print(): space-separated args + newline.
func __pytra_print(args ...interface{}) {
	parts := make([]string, len(args))
	for i, a := range args {
		parts[i] = fmt.Sprint(a)
	}
	fmt.Println(strings.Join(parts, " "))
}

// __pytra_str converts any value to string (Python str()).
func __pytra_str(v interface{}) string {
	return fmt.Sprint(v)
}

// ---------------------------------------------------------------------------
// time
// ---------------------------------------------------------------------------

var _pytra_perf_counter_start = time.Now()

// perf_counter returns seconds since an arbitrary epoch (Python time.perf_counter).
func perf_counter() float64 {
	return float64(time.Since(_pytra_perf_counter_start).Nanoseconds()) / 1e9
}

// ---------------------------------------------------------------------------
// pathlib
// ---------------------------------------------------------------------------

// Path is a minimal pathlib.Path equivalent.
func Path(s string) string {
	return s
}

// __pytra_write_text writes content to a file (Python Path.write_text).
func __pytra_write_text(path string, content string) {
	dir := filepath.Dir(path)
	if dir != "" && dir != "." {
		os.MkdirAll(dir, 0755)
	}
	os.WriteFile(path, []byte(content), 0644)
}

// ---------------------------------------------------------------------------
// numeric / container helpers
// ---------------------------------------------------------------------------

// __pytra_len returns the length of a slice or string.
func __pytra_len(v interface{}) int64 {
	switch t := v.(type) {
	case string:
		return int64(len(t))
	case []int64:
		return int64(len(t))
	case []float64:
		return int64(len(t))
	case []string:
		return int64(len(t))
	case []byte:
		return int64(len(t))
	case []interface{}:
		return int64(len(t))
	default:
		return 0
	}
}

// __pytra_abs returns the absolute value.
func __pytra_abs(v int64) int64 {
	if v < 0 {
		return -v
	}
	return v
}

// __pytra_abs_float returns the absolute value of a float.
func __pytra_abs_float(v float64) float64 {
	if v < 0 {
		return -v
	}
	return v
}

// __pytra_min returns the minimum of two int64 values.
func __pytra_min(a int64, b int64) int64 {
	if a < b {
		return a
	}
	return b
}

// __pytra_max returns the maximum of two int64 values.
func __pytra_max(a int64, b int64) int64 {
	if a > b {
		return a
	}
	return b
}

// __pytra_floordiv performs Python-style floor division.
func __pytra_floordiv(a int64, b int64) int64 {
	q := a / b
	if (a^b) < 0 && q*b != a {
		q -= 1
	}
	return q
}

// __pytra_contains checks if needle is in haystack (Python `in` operator).
func __pytra_contains(haystack interface{}, needle interface{}) bool {
	switch h := haystack.(type) {
	case string:
		n, ok := needle.(string)
		if ok {
			return strings.Contains(h, n)
		}
	case []int64:
		n, ok := needle.(int64)
		if ok {
			for _, v := range h {
				if v == n {
					return true
				}
			}
		}
	}
	return false
}

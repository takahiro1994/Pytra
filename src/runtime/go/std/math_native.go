// math_native.go: @extern delegation for pytra.std.math + pytra.std.random.
// Hand-written native implementation.
package main

import (
	"math"
	"math/rand"
	"time"
)

func __pytra_sqrt(x interface{}) float64  { return math.Sqrt(_toF64(x)) }
func __pytra_sin(x interface{}) float64   { return math.Sin(_toF64(x)) }
func __pytra_cos(x interface{}) float64   { return math.Cos(_toF64(x)) }
func __pytra_tan(x interface{}) float64   { return math.Tan(_toF64(x)) }
func __pytra_atan2(y, x interface{}) float64 { return math.Atan2(_toF64(y), _toF64(x)) }
func __pytra_floor(x interface{}) float64 { return math.Floor(_toF64(x)) }
func __pytra_ceil(x interface{}) float64  { return math.Ceil(_toF64(x)) }
func __pytra_pow(x, y interface{}) float64 { return math.Pow(_toF64(x), _toF64(y)) }
func __pytra_exp(x interface{}) float64   { return math.Exp(_toF64(x)) }
func __pytra_log(x interface{}) float64   { return math.Log(_toF64(x)) }
func __pytra_fabs(x interface{}) float64  { return math.Abs(_toF64(x)) }
func __pytra_pi() float64                 { return math.Pi }

var _pytra_rng = rand.New(rand.NewSource(time.Now().UnixNano()))

func __pytra_random() float64         { return _pytra_rng.Float64() }
func __pytra_randint(a, b int64) int64 { return a + _pytra_rng.Int63n(b-a+1) }
func __pytra_seed(s int64)            { _pytra_rng = rand.New(rand.NewSource(s)) }

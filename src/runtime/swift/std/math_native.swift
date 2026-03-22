// Generated std/math.swift delegates host bindings through this native seam.

#if canImport(Darwin)
import Foundation
private func _sqrt(_ x: Double) -> Double { return Foundation.sqrt(x) }
private func _sin(_ x: Double) -> Double { return Foundation.sin(x) }
private func _cos(_ x: Double) -> Double { return Foundation.cos(x) }
private func _tan(_ x: Double) -> Double { return Foundation.tan(x) }
private func _exp(_ x: Double) -> Double { return Foundation.exp(x) }
private func _log(_ x: Double) -> Double { return Foundation.log(x) }
private func _log10(_ x: Double) -> Double { return Foundation.log10(x) }
private func _fabs(_ x: Double) -> Double { return Foundation.fabs(x) }
private func _floor(_ x: Double) -> Double { return Foundation.floor(x) }
private func _ceil(_ x: Double) -> Double { return Foundation.ceil(x) }
private func _pow(_ x: Double, _ y: Double) -> Double { return Foundation.pow(x, y) }
#else
import Glibc
private func _sqrt(_ x: Double) -> Double { return Glibc.sqrt(x) }
private func _sin(_ x: Double) -> Double { return Glibc.sin(x) }
private func _cos(_ x: Double) -> Double { return Glibc.cos(x) }
private func _tan(_ x: Double) -> Double { return Glibc.tan(x) }
private func _exp(_ x: Double) -> Double { return Glibc.exp(x) }
private func _log(_ x: Double) -> Double { return Glibc.log(x) }
private func _log10(_ x: Double) -> Double { return Glibc.log10(x) }
private func _fabs(_ x: Double) -> Double { return Glibc.fabs(x) }
private func _floor(_ x: Double) -> Double { return Glibc.floor(x) }
private func _ceil(_ x: Double) -> Double { return Glibc.ceil(x) }
private func _pow(_ x: Double, _ y: Double) -> Double { return Glibc.pow(x, y) }
#endif

func math_native_pi() -> Double { return Double.pi }
func math_native_e() -> Double { return 2.718281828459045 }
func math_native_sqrt(_ x: Double) -> Double { return _sqrt(x) }
func math_native_sin(_ x: Double) -> Double { return _sin(x) }
func math_native_cos(_ x: Double) -> Double { return _cos(x) }
func math_native_tan(_ x: Double) -> Double { return _tan(x) }
func math_native_exp(_ x: Double) -> Double { return _exp(x) }
func math_native_log(_ x: Double) -> Double { return _log(x) }
func math_native_log10(_ x: Double) -> Double { return _log10(x) }
func math_native_fabs(_ x: Double) -> Double { return _fabs(x) }
func math_native_floor(_ x: Double) -> Double { return _floor(x) }
func math_native_ceil(_ x: Double) -> Double { return _ceil(x) }
func math_native_pow(_ x: Double, _ y: Double) -> Double { return _pow(x, y) }

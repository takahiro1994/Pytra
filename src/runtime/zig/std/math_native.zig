// Pytra Zig runtime: math native bindings.
// Generated std/math.zig delegates host bindings through this native seam.

const std = @import("std");

pub const pi: f64 = std.math.pi;
pub const e: f64 = std.math.e;

pub fn sqrt(x: f64) f64 {
    return std.math.sqrt(x);
}

pub fn sin(x: f64) f64 {
    return std.math.sin(x);
}

pub fn cos(x: f64) f64 {
    return std.math.cos(x);
}

pub fn tan(x: f64) f64 {
    return std.math.tan(x);
}

pub fn asin(x: f64) f64 {
    return std.math.asin(x);
}

pub fn acos(x: f64) f64 {
    return std.math.acos(x);
}

pub fn atan(x: f64) f64 {
    return std.math.atan(x);
}

pub fn atan2(y: f64, x: f64) f64 {
    return std.math.atan2(y, x);
}

pub fn exp(x: f64) f64 {
    return @exp(x);
}

pub fn log(x: f64) f64 {
    return @log(x);
}

pub fn log2(x: f64) f64 {
    return std.math.log2(x);
}

pub fn log10(x: f64) f64 {
    return std.math.log10(x);
}

pub fn fabs(x: f64) f64 {
    return @abs(x);
}

pub fn floor(x: f64) f64 {
    return @floor(x);
}

pub fn ceil(x: f64) f64 {
    return @ceil(x);
}

pub fn pow(x: f64, y: f64) f64 {
    return std.math.pow(f64, x, y);
}

pub fn fmod(x: f64, y: f64) f64 {
    return @mod(x, y);
}

pub fn hypot(x: f64, y: f64) f64 {
    return std.math.hypot(x, y);
}

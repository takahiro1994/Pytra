// Native implementation of pytra.std.pathlib for Zig.
//
// Provides Path type that works with Zig's []const u8 strings.
// This avoids the PyObject = i64 limitation for string-based types.
//
// source: src/pytra/std/pathlib.py

const std = @import("std");
const pytra = @import("../built_in/py_runtime.zig");
const os_native = @import("os_native.zig");
const os_path_native = @import("os_path_native.zig");

pub const Path = struct {
    _value: []const u8,

    pub fn init(value: []const u8) Path {
        return Path{ ._value = value };
    }

    pub fn __str__(self: *const Path) []const u8 {
        return self._value;
    }

    pub fn __repr__(self: *const Path) []const u8 {
        _ = self;
        return "Path(...)";
    }

    pub fn __fspath__(self: *const Path) []const u8 {
        return self._value;
    }

    pub fn __truediv__(self: *const Path, rhs: []const u8) *Path {
        return pytra.make_object(Path, Path.init(os_path_native.join(self._value, rhs)));
    }

    pub fn parent(self: *const Path) *Path {
        const d = os_path_native.dirname(self._value);
        const result = if (d.len == 0) "." else d;
        return pytra.make_object(Path, Path.init(result));
    }

    pub fn name(self: *const Path) []const u8 {
        return os_path_native.basename(self._value);
    }

    pub fn suffix(self: *const Path) []const u8 {
        const bn = os_path_native.basename(self._value);
        if (std.mem.lastIndexOfScalar(u8, bn, '.')) |dot| {
            return bn[dot..];
        }
        return "";
    }

    pub fn stem(self: *const Path) []const u8 {
        const bn = os_path_native.basename(self._value);
        if (std.mem.lastIndexOfScalar(u8, bn, '.')) |dot| {
            return bn[0..dot];
        }
        return bn;
    }

    pub fn exists(self: *const Path) bool {
        return os_path_native.exists(self._value);
    }

    pub fn mkdir(self: *const Path, _: bool, _: bool) void {
        os_native.mkdir(self._value, false);
    }

    pub fn read_text(self: *const Path, _: []const u8) []const u8 {
        _ = self;
        return "";
    }

    pub fn write_text(self: *const Path, text: []const u8, _: []const u8) void {
        const f = std.fs.cwd().createFile(self._value, .{}) catch return;
        defer f.close();
        f.writeAll(text) catch {};
    }

    pub fn resolve(self: *const Path) *Path {
        return pytra.make_object(Path, Path.init(self._value));
    }
};

// Pytra Zig runtime – minimal built-in helpers.
// This file is loaded by generated Zig programs via @import("py_runtime.zig").

const std = @import("std");

/// Print values separated by spaces, Python-style.
pub fn print(args: anytype) void {
    const writer = std.io.getStdOut().writer();
    inline for (args, 0..) |arg, i| {
        if (i > 0) writer.writeAll(" ") catch {};
        printValue(writer, arg);
    }
    writer.writeAll("\n") catch {};
}

fn printValue(writer: anytype, value: anytype) void {
    const T = @TypeOf(value);
    switch (@typeInfo(T)) {
        .Int, .ComptimeInt => {
            writer.print("{d}", .{value}) catch {};
        },
        .Float, .ComptimeFloat => {
            writer.print("{d}", .{value}) catch {};
        },
        .Bool => {
            writer.writeAll(if (value) "True" else "False") catch {};
        },
        .Pointer => |ptr_info| {
            if (ptr_info.size == .Slice and ptr_info.child == u8) {
                writer.writeAll(value) catch {};
            } else {
                writer.print("{any}", .{value}) catch {};
            }
        },
        .Optional => {
            if (value) |v| {
                printValue(writer, v);
            } else {
                writer.writeAll("None") catch {};
            }
        },
        .Null => {
            writer.writeAll("None") catch {};
        },
        else => {
            writer.print("{any}", .{value}) catch {};
        },
    }
}

/// Python-style truthiness check.
pub fn truthy(value: anytype) bool {
    const T = @TypeOf(value);
    switch (@typeInfo(T)) {
        .Bool => return value,
        .Int, .ComptimeInt => return value != 0,
        .Float, .ComptimeFloat => return value != 0.0,
        .Optional => return value != null,
        .Null => return false,
        .Pointer => |ptr_info| {
            if (ptr_info.size == .Slice) {
                return value.len > 0;
            }
            return true;
        },
        else => return true,
    }
}

/// Convert a value to string representation.
pub fn to_str(value: anytype) []const u8 {
    _ = value;
    return "<value>";
}

/// Concatenate two strings.
pub fn str_concat(a: []const u8, b: []const u8) []const u8 {
    _ = a;
    _ = b;
    return "<concat>";
}

/// Join multiple strings.
pub fn str_join(parts: anytype) []const u8 {
    _ = parts;
    return "<join>";
}

/// Create a new empty dict (stub).
pub fn new_dict() void {
    return;
}

/// isinstance check (stub).
pub fn isinstance_check(obj: anytype, typ: anytype) bool {
    _ = obj;
    _ = typ;
    return false;
}

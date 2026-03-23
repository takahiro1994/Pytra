import java.nio.file.{Files, Paths}
import scala.collection.mutable
import scala.util.boundary, boundary.break

// --- module: pytra.std.math ---


def sqrt(x: Double): Double = {
    return math_native.sqrt(x)
}

def sin(x: Double): Double = {
    return math_native.sin(x)
}

def cos(x: Double): Double = {
    return math_native.cos(x)
}

def tan(x: Double): Double = {
    return math_native.tan(x)
}

def exp(x: Double): Double = {
    return math_native.exp(x)
}

def log(x: Double): Double = {
    return math_native.log(x)
}

def log10(x: Double): Double = {
    return math_native.log10(x)
}

def fabs(x: Double): Double = {
    return math_native.fabs(x)
}

def floor(x: Double): Double = {
    return math_native.floor(x)
}

def ceil(x: Double): Double = {
    return math_native.ceil(x)
}

def pow(x: Double, y: Double): Double = {
    return math_native.pow(x, y)
}
// --- module: pytra.std.time ---


def perf_counter(): Double = {
    return time_native.perf_counter()
}
// --- module: pytra.utils.png ---


def _png_append_list(dst: mutable.ArrayBuffer[Long], src: mutable.ArrayBuffer[Long]): Unit = {
    var i: Long = 0L
    var n: Long = __pytra_len(src)
    while (i < n) {
        dst.append(__pytra_int(__pytra_get_index(src, i)))
        i += 1L
    }
}

def _crc32(data: mutable.ArrayBuffer[Long]): Long = {
    var crc: Long = 4294967295L
    var poly: Long = 3988292384L
    val __iter_0 = __pytra_as_list(data)
    var __i_1: Long = 0L
    while (__i_1 < __iter_0.size.toLong) {
        val b: Long = __pytra_int(__iter_0(__i_1.toInt))
        crc = crc ^ b
        var i: Long = 0L
        while (i < 8L) {
            var lowbit: Long = crc & 1L
            if (lowbit != 0L) {
                crc = (crc >> 1L ^ poly)
            } else {
                crc = crc >> 1L
            }
            i += 1L
        }
        __i_1 += 1L
    }
    return crc ^ 4294967295L
}

def _adler32(data: mutable.ArrayBuffer[Long]): Long = {
    var mod: Long = 65521L
    var s1: Long = 1L
    var s2: Long = 0L
    val __iter_0 = __pytra_as_list(data)
    var __i_1: Long = 0L
    while (__i_1 < __iter_0.size.toLong) {
        val b: Long = __pytra_int(__iter_0(__i_1.toInt))
        s1 += b
        if (s1 >= mod) {
            s1 -= mod
        }
        s2 += s1
        s2 = s2 % mod
        __i_1 += 1L
    }
    return (((s2 << 16L | s1)) & 4294967295L)
}

def _png_u16le(v: Long): mutable.ArrayBuffer[Long] = {
    return __pytra_as_list(mutable.ArrayBuffer[Long](v & 255L, (v >> 8L & 255L))).asInstanceOf[mutable.ArrayBuffer[Long]]
}

def _png_u32be(v: Long): mutable.ArrayBuffer[Long] = {
    return __pytra_as_list(mutable.ArrayBuffer[Long]((v >> 24L & 255L), (v >> 16L & 255L), (v >> 8L & 255L), v & 255L)).asInstanceOf[mutable.ArrayBuffer[Long]]
}

def _zlib_deflate_store(data: mutable.ArrayBuffer[Long]): mutable.ArrayBuffer[Long] = {
    var out: mutable.ArrayBuffer[Long] = __pytra_as_list(mutable.ArrayBuffer[Long]()).asInstanceOf[mutable.ArrayBuffer[Long]]
    _png_append_list(out, mutable.ArrayBuffer[Long](120L, 1L))
    var n: Long = __pytra_len(data)
    var pos: Long = 0L
    while (pos < n) {
        var remain: Long = n - pos
        var chunk_len: Long = __pytra_int(__pytra_ifexp((remain > 65535L), 65535L, remain))
        var py_final: Long = __pytra_int(__pytra_ifexp((pos + chunk_len >= n), 1L, 0L))
        out.append(py_final)
        _png_append_list(out, _png_u16le(chunk_len))
        _png_append_list(out, _png_u16le(65535L ^ chunk_len))
        var i: Long = pos
        var end: Long = pos + chunk_len
        while (i < end) {
            out.append(__pytra_int(__pytra_get_index(data, i)))
            i += 1L
        }
        pos += chunk_len
    }
    _png_append_list(out, _png_u32be(_adler32(data)))
    return out
}

def _chunk(chunk_type: mutable.ArrayBuffer[Long], data: mutable.ArrayBuffer[Long]): mutable.ArrayBuffer[Long] = {
    var crc_input: mutable.ArrayBuffer[Long] = __pytra_as_list(mutable.ArrayBuffer[Long]()).asInstanceOf[mutable.ArrayBuffer[Long]]
    _png_append_list(crc_input, chunk_type)
    _png_append_list(crc_input, data)
    var crc: Long = _crc32(crc_input) & 4294967295L
    var out: mutable.ArrayBuffer[Long] = __pytra_as_list(mutable.ArrayBuffer[Long]()).asInstanceOf[mutable.ArrayBuffer[Long]]
    _png_append_list(out, _png_u32be(__pytra_len(data)))
    _png_append_list(out, chunk_type)
    _png_append_list(out, data)
    _png_append_list(out, _png_u32be(crc))
    return out
}

def write_rgb_png(path: String, width: Long, height: Long, pixels: mutable.ArrayBuffer[Long]): Unit = {
    var raw: mutable.ArrayBuffer[Long] = __pytra_as_list(mutable.ArrayBuffer[Long]()).asInstanceOf[mutable.ArrayBuffer[Long]]
    val __iter_0 = __pytra_as_list(pixels)
    var __i_1: Long = 0L
    while (__i_1 < __iter_0.size.toLong) {
        val b: Long = __pytra_int(__iter_0(__i_1.toInt))
        raw.append(b)
        __i_1 += 1L
    }
    var expected: Long = (width * height * 3L)
    if (__pytra_len(raw) != expected) {
        throw new RuntimeException(__pytra_str((__pytra_str(__pytra_str(__pytra_str("pixels length mismatch: got=") + __pytra_str(__pytra_len(raw))) + __pytra_str(" expected=")) + __pytra_str(expected))))
    }
    var scanlines: mutable.ArrayBuffer[Long] = __pytra_as_list(mutable.ArrayBuffer[Long]()).asInstanceOf[mutable.ArrayBuffer[Long]]
    var row_bytes: Long = width * 3L
    var y: Long = 0L
    while (y < height) {
        scanlines.append(0L)
        var start: Long = y * row_bytes
        var end: Long = start + row_bytes
        var i: Long = start
        while (i < end) {
            scanlines.append(__pytra_int(__pytra_get_index(raw, i)))
            i += 1L
        }
        y += 1L
    }
    var ihdr: mutable.ArrayBuffer[Long] = __pytra_as_list(mutable.ArrayBuffer[Long]()).asInstanceOf[mutable.ArrayBuffer[Long]]
    _png_append_list(ihdr, _png_u32be(width))
    _png_append_list(ihdr, _png_u32be(height))
    _png_append_list(ihdr, mutable.ArrayBuffer[Long](8L, 2L, 0L, 0L, 0L))
    var idat: mutable.ArrayBuffer[Long] = _zlib_deflate_store(scanlines)
    var png: mutable.ArrayBuffer[Long] = __pytra_as_list(mutable.ArrayBuffer[Long]()).asInstanceOf[mutable.ArrayBuffer[Long]]
    _png_append_list(png, mutable.ArrayBuffer[Long](137L, 80L, 78L, 71L, 13L, 10L, 26L, 10L))
    _png_append_list(png, _chunk(mutable.ArrayBuffer[Long](73L, 72L, 68L, 82L), ihdr))
    _png_append_list(png, _chunk(mutable.ArrayBuffer[Long](73L, 68L, 65L, 84L), idat))
    var iend_data: mutable.ArrayBuffer[Long] = __pytra_as_list(mutable.ArrayBuffer[Long]()).asInstanceOf[mutable.ArrayBuffer[Long]]
    _png_append_list(png, _chunk(mutable.ArrayBuffer[Long](73L, 69L, 78L, 68L), iend_data))
    var f: PyFile = open(path, "wb")
    try {
        f.write(__pytra_bytes(png))
    } finally {
        f.close()
    }
}


// 02: Sample that runs a mini sphere-only ray tracer and outputs a PNG image.
// Dependencies are kept minimal (time only) for transpilation compatibility.

def clamp01(v: Double): Double = {
    if (v < 0.0) {
        return 0.0
    }
    if (v > 1.0) {
        return 1.0
    }
    return v
}

def hit_sphere(ox: Double, oy: Double, oz: Double, dx: Double, dy: Double, dz: Double, cx: Double, cy: Double, cz: Double, r: Double): Double = {
    var lx: Double = ox - cx
    var ly: Double = oy - cy
    var lz: Double = oz - cz
    var a: Double = ((dx * dx + dy * dy) + dz * dz)
    var b: Double = (2.0 * (((lx * dx + ly * dy) + lz * dz)))
    var c: Double = (((lx * lx + ly * ly) + lz * lz) - r * r)
    var d: Double = (b * b - (4.0 * a * c))
    if (d < 0.0) {
        return __pytra_float(-1.0)
    }
    var sd: Double = math_native.sqrt(d)
    var t0: Double = ((((-b) - sd)) / (2.0 * a))
    var t1: Double = ((((-b) + sd)) / (2.0 * a))
    if (t0 > 0.001) {
        return t0
    }
    if (t1 > 0.001) {
        return t1
    }
    return __pytra_float(-1.0)
}

def render(width: Long, height: Long, aa: Long): mutable.ArrayBuffer[Long] = {
    var pixels: mutable.ArrayBuffer[Long] = mutable.ArrayBuffer[Long]()
    var ox: Double = 0.0
    var oy: Double = 0.0
    var oz: Double = __pytra_float(-3.0)
    var lx: Double = __pytra_float(-0.4)
    var ly: Double = 0.8
    var lz: Double = __pytra_float(-0.45)
    var y: Long = 0L
    while (y < height) {
        var x: Long = 0L
        while (x < width) {
            var ar: Long = 0L
            var ag: Long = 0L
            var ab: Long = 0L
            var ay: Long = 0L
            while (ay < aa) {
                var ax: Long = 0L
                while (ax < aa) {
                    var fy: Double = (((__pytra_float(y) + ((__pytra_float(ay) + 0.5) / __pytra_float(aa)))) / (__pytra_float(height - 1L)))
                    var fx: Double = (((__pytra_float(x) + ((__pytra_float(ax) + 0.5) / __pytra_float(aa)))) / (__pytra_float(width - 1L)))
                    var sy: Double = (1.0 - 2.0 * fy)
                    var sx: Double = (((2.0 * fx - 1.0)) * (__pytra_float(width) / __pytra_float(height)))
                    var dx: Double = sx
                    var dy: Double = sy
                    var dz: Double = 1.0
                    var inv_len: Double = 1.0 / math_native.sqrt(((dx * dx + dy * dy) + dz * dz))
                    dx *= inv_len
                    dy *= inv_len
                    dz *= inv_len
                    var t_min: Double = 1e+30
                    var hit_id: Long = __pytra_int(-1L)
                    var t: Double = hit_sphere(ox, oy, oz, dx, dy, dz, (-0.8), (-0.2), 2.2, 0.8)
                    if ((t > 0.0) && (t < t_min)) {
                        t_min = t
                        hit_id = 0L
                    }
                    t = hit_sphere(ox, oy, oz, dx, dy, dz, 0.9, 0.1, 2.9, 0.95)
                    if ((t > 0.0) && (t < t_min)) {
                        t_min = t
                        hit_id = 1L
                    }
                    t = hit_sphere(ox, oy, oz, dx, dy, dz, 0.0, (-1001.0), 3.0, 1000.0)
                    if ((t > 0.0) && (t < t_min)) {
                        t_min = t
                        hit_id = 2L
                    }
                    var r: Long = 0L
                    var g: Long = 0L
                    var b: Long = 0L
                    if (hit_id >= 0L) {
                        var px: Double = (ox + dx * t_min)
                        var py: Double = (oy + dy * t_min)
                        var pz: Double = (oz + dz * t_min)
                        var nx: Double = 0.0
                        var ny: Double = 0.0
                        var nz: Double = 0.0
                        if (hit_id == 0L) {
                            nx = ((px + 0.8) / 0.8)
                            ny = ((py + 0.2) / 0.8)
                            nz = ((pz - 2.2) / 0.8)
                        } else {
                            if (hit_id == 1L) {
                                nx = ((px - 0.9) / 0.95)
                                ny = ((py - 0.1) / 0.95)
                                nz = ((pz - 2.9) / 0.95)
                            } else {
                                nx = 0.0
                                ny = 1.0
                                nz = 0.0
                            }
                        }
                        var diff: Double = (((nx * (-lx)) + (ny * (-ly))) + (nz * (-lz)))
                        diff = clamp01(diff)
                        var base_r: Double = 0.0
                        var base_g: Double = 0.0
                        var base_b: Double = 0.0
                        if (hit_id == 0L) {
                            base_r = 0.95
                            base_g = 0.35
                            base_b = 0.25
                        } else {
                            if (hit_id == 1L) {
                                base_r = 0.25
                                base_g = 0.55
                                base_b = 0.95
                            } else {
                                var checker: Long = __pytra_int((px + 50.0) * 0.8) + __pytra_int((pz + 50.0) * 0.8)
                                if (checker % 2L == 0L) {
                                    base_r = 0.85
                                    base_g = 0.85
                                    base_b = 0.85
                                } else {
                                    base_r = 0.2
                                    base_g = 0.2
                                    base_b = 0.2
                                }
                            }
                        }
                        var shade: Double = (0.12 + 0.88 * diff)
                        r = __pytra_int(255.0 * clamp01(base_r * shade))
                        g = __pytra_int(255.0 * clamp01(base_g * shade))
                        b = __pytra_int(255.0 * clamp01(base_b * shade))
                    } else {
                        var tsky: Double = (0.5 * (dy + 1.0))
                        r = __pytra_int(255.0 * ((0.65 + 0.2 * tsky)))
                        g = __pytra_int(255.0 * ((0.75 + 0.18 * tsky)))
                        b = __pytra_int(255.0 * ((0.9 + 0.08 * tsky)))
                    }
                    ar += r
                    ag += g
                    ab += b
                    ax += 1L
                }
                ay += 1L
            }
            var samples: Long = aa * aa
            pixels.append(__pytra_int(ar / samples))
            pixels.append(__pytra_int(ag / samples))
            pixels.append(__pytra_int(ab / samples))
            x += 1L
        }
        y += 1L
    }
    return pixels
}

def run_raytrace(): Unit = {
    var width: Long = 1600L
    var height: Long = 900L
    var aa: Long = 2L
    var out_path: String = "sample/out/02_raytrace_spheres.png"
    var start: Double = __pytra_perf_counter()
    var pixels: mutable.ArrayBuffer[Long] = render(width, height, aa)
    write_rgb_png(out_path, width, height, pixels)
    var elapsed: Double = __pytra_perf_counter() - start
    __pytra_print("output:", out_path)
    __pytra_print("size:", width, "x", height)
    __pytra_print("elapsed_sec:", elapsed)
}

def main(args: Array[String]): Unit = {
    val _ = run_raytrace()
}
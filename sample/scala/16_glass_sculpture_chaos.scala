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
// --- module: pytra.utils.gif ---


def _gif_append_list(dst: mutable.ArrayBuffer[Long], src: mutable.ArrayBuffer[Long]): Unit = {
    var i: Long = 0L
    var n: Long = __pytra_len(src)
    while (i < n) {
        dst.append(__pytra_int(__pytra_get_index(src, i)))
        i += 1L
    }
}

def _gif_u16le(v: Long): mutable.ArrayBuffer[Long] = {
    return __pytra_as_list(mutable.ArrayBuffer[Long](v & 255L, (v >> 8L & 255L))).asInstanceOf[mutable.ArrayBuffer[Long]]
}

def _lzw_encode(data: mutable.ArrayBuffer[Long], min_code_size: Long): mutable.ArrayBuffer[Long] = {
    if (__pytra_len(data) == 0L) {
        var empty: mutable.ArrayBuffer[Long] = __pytra_as_list(mutable.ArrayBuffer[Long]()).asInstanceOf[mutable.ArrayBuffer[Long]]
        return __pytra_bytes(empty)
    }
    var clear_code: Long = 1L << min_code_size
    var end_code: Long = clear_code + 1L
    var code_size: Long = min_code_size + 1L
    var out: mutable.ArrayBuffer[Long] = __pytra_as_list(mutable.ArrayBuffer[Long]()).asInstanceOf[mutable.ArrayBuffer[Long]]
    var bit_buffer: Long = 0L
    var bit_count: Long = 0L
    bit_buffer += clear_code << bit_count
    bit_count += code_size
    while (bit_count >= 8L) {
        out.append(bit_buffer & 255L)
        bit_buffer = bit_buffer >> 8L
        bit_count -= 8L
    }
    code_size = min_code_size + 1L
    val __iter_0 = __pytra_as_list(data)
    var __i_1: Long = 0L
    while (__i_1 < __iter_0.size.toLong) {
        val v: Long = __pytra_int(__iter_0(__i_1.toInt))
        bit_buffer += v << bit_count
        bit_count += code_size
        while (bit_count >= 8L) {
            out.append(bit_buffer & 255L)
            bit_buffer = bit_buffer >> 8L
            bit_count -= 8L
        }
        bit_buffer += clear_code << bit_count
        bit_count += code_size
        while (bit_count >= 8L) {
            out.append(bit_buffer & 255L)
            bit_buffer = bit_buffer >> 8L
            bit_count -= 8L
        }
        code_size = min_code_size + 1L
        __i_1 += 1L
    }
    bit_buffer += end_code << bit_count
    bit_count += code_size
    while (bit_count >= 8L) {
        out.append(bit_buffer & 255L)
        bit_buffer = bit_buffer >> 8L
        bit_count -= 8L
    }
    if (bit_count > 0L) {
        out.append(bit_buffer & 255L)
    }
    return __pytra_bytes(out)
}

def grayscale_palette(): mutable.ArrayBuffer[Long] = {
    var p: mutable.ArrayBuffer[Long] = __pytra_as_list(mutable.ArrayBuffer[Long]()).asInstanceOf[mutable.ArrayBuffer[Long]]
    var i: Long = 0L
    while (i < 256L) {
        p.append(i)
        p.append(i)
        p.append(i)
        i += 1L
    }
    return __pytra_bytes(p)
}

def save_gif(path: String, width: Long, height: Long, frames: mutable.ArrayBuffer[Any], palette: mutable.ArrayBuffer[Long], delay_cs: Long, loop: Long): Unit = {
    if (__pytra_len(palette) != 256L * 3L) {
        throw new RuntimeException(__pytra_str("palette must be 256*3 bytes"))
    }
    var frame_lists: mutable.ArrayBuffer[Any] = __pytra_as_list(mutable.ArrayBuffer[Any]())
    var fr_list: mutable.ArrayBuffer[Long] = mutable.ArrayBuffer[Long]()
    var v: Long = 0L
    val __iter_0 = __pytra_as_list(frames)
    var __i_1: Long = 0L
    while (__i_1 < __iter_0.size.toLong) {
        val fr: mutable.ArrayBuffer[Long] = __pytra_as_list(__iter_0(__i_1.toInt)).asInstanceOf[mutable.ArrayBuffer[Long]]
        fr_list = __pytra_as_list(mutable.ArrayBuffer[Long]()).asInstanceOf[mutable.ArrayBuffer[Long]]
        val __iter_2 = __pytra_as_list(fr)
        var __i_3: Long = 0L
        while (__i_3 < __iter_2.size.toLong) {
            val v: Long = __pytra_int(__iter_2(__i_3.toInt))
            fr_list.append(v)
            __i_3 += 1L
        }
        if (__pytra_len(fr_list) != width * height) {
            throw new RuntimeException(__pytra_str("frame size mismatch"))
        }
        frame_lists.append(fr_list)
        __i_1 += 1L
    }
    var palette_list: mutable.ArrayBuffer[Long] = __pytra_as_list(mutable.ArrayBuffer[Long]()).asInstanceOf[mutable.ArrayBuffer[Long]]
    val __iter_4 = __pytra_as_list(palette)
    var __i_5: Long = 0L
    while (__i_5 < __iter_4.size.toLong) {
        val v: Long = __pytra_int(__iter_4(__i_5.toInt))
        palette_list.append(v)
        __i_5 += 1L
    }
    var out: mutable.ArrayBuffer[Long] = __pytra_as_list(mutable.ArrayBuffer[Long]()).asInstanceOf[mutable.ArrayBuffer[Long]]
    _gif_append_list(out, mutable.ArrayBuffer[Long](71L, 73L, 70L, 56L, 57L, 97L))
    _gif_append_list(out, _gif_u16le(width))
    _gif_append_list(out, _gif_u16le(height))
    out.append(247L)
    out.append(0L)
    out.append(0L)
    _gif_append_list(out, palette_list)
    _gif_append_list(out, mutable.ArrayBuffer[Long](33L, 255L, 11L, 78L, 69L, 84L, 83L, 67L, 65L, 80L, 69L, 50L, 46L, 48L, 3L, 1L))
    _gif_append_list(out, _gif_u16le(loop))
    out.append(0L)
    val __iter_6 = __pytra_as_list(frame_lists)
    var __i_7: Long = 0L
    while (__i_7 < __iter_6.size.toLong) {
        val fr_list: mutable.ArrayBuffer[Long] = __pytra_as_list(__iter_6(__i_7.toInt)).asInstanceOf[mutable.ArrayBuffer[Long]]
        _gif_append_list(out, mutable.ArrayBuffer[Long](33L, 249L, 4L, 0L))
        _gif_append_list(out, _gif_u16le(delay_cs))
        _gif_append_list(out, mutable.ArrayBuffer[Long](0L, 0L))
        out.append(44L)
        _gif_append_list(out, _gif_u16le(0L))
        _gif_append_list(out, _gif_u16le(0L))
        _gif_append_list(out, _gif_u16le(width))
        _gif_append_list(out, _gif_u16le(height))
        out.append(0L)
        out.append(8L)
        var compressed: mutable.ArrayBuffer[Long] = _lzw_encode(__pytra_bytes(fr_list), 8L)
        var pos: Long = 0L
        while (pos < __pytra_len(compressed)) {
            var remain: Long = __pytra_len(compressed) - pos
            var chunk_len: Long = __pytra_int(__pytra_ifexp((remain > 255L), 255L, remain))
            out.append(chunk_len)
            var i: Long = 0L
            while (i < chunk_len) {
                out.append(__pytra_int(__pytra_get_index(compressed, pos + i)))
                i += 1L
            }
            pos += chunk_len
        }
        out.append(0L)
        __i_7 += 1L
    }
    out.append(59L)
    var f: PyFile = open(path, "wb")
    try {
        f.write(__pytra_bytes(out))
    } finally {
        f.close()
    }
}


// 16: Sample that ray-traces chaotic rotation of glass sculptures and outputs a GIF.

def clamp01(v: Double): Double = {
    if (v < 0.0) {
        return 0.0
    }
    if (v > 1.0) {
        return 1.0
    }
    return v
}

def dot(ax: Double, ay: Double, az: Double, bx: Double, by: Double, bz: Double): Double = {
    return ((ax * bx + ay * by) + az * bz)
}

def length(x: Double, y: Double, z: Double): Double = {
    return math_native.sqrt(((x * x + y * y) + z * z))
}

def normalize(x: Double, y: Double, z: Double): mutable.ArrayBuffer[Double] = {
    var l: Double = length(x, y, z)
    if (l < 1e-09) {
        return __pytra_as_list(mutable.ArrayBuffer[Double](0.0, 0.0, 0.0)).asInstanceOf[mutable.ArrayBuffer[Double]]
    }
    return __pytra_as_list(mutable.ArrayBuffer[Double](x / l, y / l, z / l)).asInstanceOf[mutable.ArrayBuffer[Double]]
}

def reflect(ix: Double, iy: Double, iz: Double, nx: Double, ny: Double, nz: Double): mutable.ArrayBuffer[Double] = {
    var d: Double = dot(ix, iy, iz, nx, ny, nz) * 2.0
    return __pytra_as_list(mutable.ArrayBuffer[Double]((ix - d * nx), (iy - d * ny), (iz - d * nz))).asInstanceOf[mutable.ArrayBuffer[Double]]
}

def refract(ix: Double, iy: Double, iz: Double, nx: Double, ny: Double, nz: Double, eta: Double): mutable.ArrayBuffer[Double] = {
    var cosi: Double = __pytra_float(-dot(ix, iy, iz, nx, ny, nz))
    var sint2: Double = (eta * eta * ((1.0 - cosi * cosi)))
    if (sint2 > 1.0) {
        return reflect(ix, iy, iz, nx, ny, nz)
    }
    var cost: Double = math_native.sqrt(1.0 - sint2)
    var k: Double = (eta * cosi - cost)
    return __pytra_as_list(mutable.ArrayBuffer[Double]((eta * ix + k * nx), (eta * iy + k * ny), (eta * iz + k * nz))).asInstanceOf[mutable.ArrayBuffer[Double]]
}

def schlick(cos_theta: Double, f0: Double): Double = {
    var m: Double = 1.0 - cos_theta
    return (f0 + ((1.0 - f0) * (((m * m * m) * m) * m)))
}

def sky_color(dx: Double, dy: Double, dz: Double, tphase: Double): mutable.ArrayBuffer[Double] = {
    var t: Double = (0.5 * (dy + 1.0))
    var r: Double = (0.06 + 0.2 * t)
    var g: Double = (0.1 + 0.25 * t)
    var b: Double = (0.16 + 0.45 * t)
    var band: Double = (0.5 + 0.5 * math_native.sin(((8.0 * dx + 6.0 * dz) + tphase)))
    r += 0.08 * band
    g += 0.05 * band
    b += 0.12 * band
    return __pytra_as_list(mutable.ArrayBuffer[Double](clamp01(r), clamp01(g), clamp01(b))).asInstanceOf[mutable.ArrayBuffer[Double]]
}

def sphere_intersect(ox: Double, oy: Double, oz: Double, dx: Double, dy: Double, dz: Double, cx: Double, cy: Double, cz: Double, radius: Double): Double = {
    var lx: Double = ox - cx
    var ly: Double = oy - cy
    var lz: Double = oz - cz
    var b: Double = ((lx * dx + ly * dy) + lz * dz)
    var c: Double = (((lx * lx + ly * ly) + lz * lz) - radius * radius)
    var h: Double = (b * b - c)
    if (h < 0.0) {
        return __pytra_float(-1.0)
    }
    var s: Double = math_native.sqrt(h)
    var t0: Double = ((-b) - s)
    if (t0 > 0.0001) {
        return t0
    }
    var t1: Double = ((-b) + s)
    if (t1 > 0.0001) {
        return t1
    }
    return __pytra_float(-1.0)
}

def palette_332(): mutable.ArrayBuffer[Long] = {
    var p: mutable.ArrayBuffer[Long] = __pytra_bytearray(256L * 3L)
    var i: Long = 0L
    while (i < 256L) {
        var r: Long = (i >> 5L & 7L)
        var g: Long = (i >> 2L & 7L)
        var b: Long = i & 3L
        __pytra_set_index(p, (i * 3L + 0L), __pytra_int(__pytra_float(255L * r) / __pytra_float(7L)))
        __pytra_set_index(p, (i * 3L + 1L), __pytra_int(__pytra_float(255L * g) / __pytra_float(7L)))
        __pytra_set_index(p, (i * 3L + 2L), __pytra_int(__pytra_float(255L * b) / __pytra_float(3L)))
        i += 1L
    }
    return __pytra_bytes(p)
}

def quantize_332(r: Double, g: Double, b: Double): Long = {
    var rr: Long = __pytra_int(clamp01(r) * 255.0)
    var gg: Long = __pytra_int(clamp01(g) * 255.0)
    var bb: Long = __pytra_int(clamp01(b) * 255.0)
    return ((((rr >> 5L << 5L)) + ((gg >> 5L << 2L))) + (bb >> 6L))
}

def render_frame(width: Long, height: Long, frame_id: Long, frames_n: Long): mutable.ArrayBuffer[Long] = {
    var t: Double = __pytra_float(frame_id) / __pytra_float(frames_n)
    var tphase: Double = (2.0 * math_native.pi * t)
    var cam_r: Double = 3.0
    var cam_x: Double = cam_r * math_native.cos(__pytra_float(tphase) * 0.9)
    var cam_y: Double = (1.1 + 0.25 * math_native.sin(__pytra_float(tphase) * 0.6))
    var cam_z: Double = cam_r * math_native.sin(__pytra_float(tphase) * 0.9)
    var look_x: Double = 0.0
    var look_y: Double = 0.35
    var look_z: Double = 0.0
    val __tuple_0 = __pytra_as_list(normalize(look_x - cam_x, look_y - cam_y, look_z - cam_z))
    var fwd_x: Double = __pytra_float(__tuple_0(0))
    var fwd_y: Double = __pytra_float(__tuple_0(1))
    var fwd_z: Double = __pytra_float(__tuple_0(2))
    val __tuple_1 = __pytra_as_list(normalize(fwd_z, 0.0, (-fwd_x)))
    var right_x: Double = __pytra_float(__tuple_1(0))
    var right_y: Double = __pytra_float(__tuple_1(1))
    var right_z: Double = __pytra_float(__tuple_1(2))
    val __tuple_2 = __pytra_as_list(normalize((right_y * fwd_z - right_z * fwd_y), (right_z * fwd_x - right_x * fwd_z), (right_x * fwd_y - right_y * fwd_x)))
    var up_x: Double = __pytra_float(__tuple_2(0))
    var up_y: Double = __pytra_float(__tuple_2(1))
    var up_z: Double = __pytra_float(__tuple_2(2))
    var s0x: Double = 0.9 * math_native.cos(1.3 * __pytra_float(tphase))
    var s0y: Double = (0.15 + 0.35 * math_native.sin(1.7 * __pytra_float(tphase)))
    var s0z: Double = 0.9 * math_native.sin(1.3 * __pytra_float(tphase))
    var s1x: Double = 1.2 * math_native.cos((1.3 * __pytra_float(tphase) + 2.094))
    var s1y: Double = (0.1 + 0.4 * math_native.sin((1.1 * __pytra_float(tphase) + 0.8)))
    var s1z: Double = 1.2 * math_native.sin((1.3 * __pytra_float(tphase) + 2.094))
    var s2x: Double = 1.0 * math_native.cos((1.3 * __pytra_float(tphase) + 4.188))
    var s2y: Double = (0.2 + 0.3 * math_native.sin((1.5 * __pytra_float(tphase) + 1.9)))
    var s2z: Double = 1.0 * math_native.sin((1.3 * __pytra_float(tphase) + 4.188))
    var lr: Double = 0.35
    var lx: Double = 2.4 * math_native.cos(__pytra_float(tphase) * 1.8)
    var ly: Double = (1.8 + 0.8 * math_native.sin(__pytra_float(tphase) * 1.2))
    var lz: Double = 2.4 * math_native.sin(__pytra_float(tphase) * 1.8)
    var frame: mutable.ArrayBuffer[Long] = __pytra_bytearray(width * height)
    var aspect: Double = __pytra_float(width) / __pytra_float(height)
    var fov: Double = 1.25
    var py: Long = 0L
    while (py < height) {
        var row_base: Long = py * width
        var sy: Double = (1.0 - ((2.0 * (__pytra_float(py) + 0.5)) / __pytra_float(height)))
        var px: Long = 0L
        while (px < width) {
            var sx: Double = (((((2.0 * (__pytra_float(px) + 0.5)) / __pytra_float(width)) - 1.0)) * aspect)
            var rx: Double = (fwd_x + (fov * ((sx * right_x + sy * up_x))))
            var ry: Double = (fwd_y + (fov * ((sx * right_y + sy * up_y))))
            var rz: Double = (fwd_z + (fov * ((sx * right_z + sy * up_z))))
            val __tuple_5 = __pytra_as_list(normalize(rx, ry, rz))
            var dx: Double = __pytra_float(__tuple_5(0))
            var dy: Double = __pytra_float(__tuple_5(1))
            var dz: Double = __pytra_float(__tuple_5(2))
            var best_t: Double = 1000000000.0
            var hit_kind: Long = 0L
            var r: Double = 0.0
            var g: Double = 0.0
            var b: Double = 0.0
            if (dy < (-1e-06)) {
                var tf: Double = ((((-1.2) - cam_y)) / dy)
                if ((tf > 0.0001) && (tf < best_t)) {
                    best_t = tf
                    hit_kind = 1L
                }
            }
            var t0: Double = sphere_intersect(cam_x, cam_y, cam_z, dx, dy, dz, s0x, s0y, s0z, 0.65)
            if ((t0 > 0.0) && (t0 < best_t)) {
                best_t = t0
                hit_kind = 2L
            }
            var t1: Double = sphere_intersect(cam_x, cam_y, cam_z, dx, dy, dz, s1x, s1y, s1z, 0.72)
            if ((t1 > 0.0) && (t1 < best_t)) {
                best_t = t1
                hit_kind = 3L
            }
            var t2: Double = sphere_intersect(cam_x, cam_y, cam_z, dx, dy, dz, s2x, s2y, s2z, 0.58)
            if ((t2 > 0.0) && (t2 < best_t)) {
                best_t = t2
                hit_kind = 4L
            }
            var glow: Double = 0.0
            var hx: Double = 0.0
            var hz: Double = 0.0
            var ldx: Double = 0.0
            var ldy: Double = 0.0
            var ldz: Double = 0.0
            var lxv: Double = 0.0
            var lyv: Double = 0.0
            var lzv: Double = 0.0
            var ndotl: Double = 0.0
            if (hit_kind == 0L) {
                val __tuple_6 = __pytra_as_list(sky_color(dx, dy, dz, tphase))
                r = __pytra_float(__tuple_6(0))
                g = __pytra_float(__tuple_6(1))
                b = __pytra_float(__tuple_6(2))
            } else {
                if (hit_kind == 1L) {
                    hx = (cam_x + best_t * dx)
                    hz = (cam_z + best_t * dz)
                    var cx_i: Long = __pytra_int(math_native.floor(hx * 2.0))
                    var cz_i: Long = __pytra_int(math_native.floor(hz * 2.0))
                    var checker: Long = __pytra_int(__pytra_ifexp((((cx_i + cz_i) % 2L) == 0L), 0L, 1L))
                    var base_r: Double = __pytra_float(__pytra_ifexp((checker == 0L), 0.1, 0.04))
                    var base_g: Double = __pytra_float(__pytra_ifexp((checker == 0L), 0.11, 0.05))
                    var base_b: Double = __pytra_float(__pytra_ifexp((checker == 0L), 0.13, 0.08))
                    lxv = lx - hx
                    lyv = (ly - (-1.2))
                    lzv = lz - hz
                    val __tuple_7 = __pytra_as_list(normalize(lxv, lyv, lzv))
                    ldx = __pytra_float(__tuple_7(0))
                    ldy = __pytra_float(__tuple_7(1))
                    ldz = __pytra_float(__tuple_7(2))
                    ndotl = __pytra_max(ldy, 0.0)
                    var ldist2: Double = ((lxv * lxv + lyv * lyv) + lzv * lzv)
                    glow = (8.0 / (1.0 + ldist2))
                    r = ((base_r + 0.8 * glow) + 0.2 * ndotl)
                    g = ((base_g + 0.5 * glow) + 0.18 * ndotl)
                    b = ((base_b + 1.0 * glow) + 0.24 * ndotl)
                } else {
                    var cx: Double = 0.0
                    var cy: Double = 0.0
                    var cz: Double = 0.0
                    var rad: Double = 1.0
                    if (hit_kind == 2L) {
                        cx = s0x
                        cy = s0y
                        cz = s0z
                        rad = 0.65
                    } else {
                        if (hit_kind == 3L) {
                            cx = s1x
                            cy = s1y
                            cz = s1z
                            rad = 0.72
                        } else {
                            cx = s2x
                            cy = s2y
                            cz = s2z
                            rad = 0.58
                        }
                    }
                    hx = (cam_x + best_t * dx)
                    var hy: Double = (cam_y + best_t * dy)
                    hz = (cam_z + best_t * dz)
                    val __tuple_8 = __pytra_as_list(normalize(((hx - cx) / rad), ((hy - cy) / rad), ((hz - cz) / rad)))
                    var nx: Double = __pytra_float(__tuple_8(0))
                    var ny: Double = __pytra_float(__tuple_8(1))
                    var nz: Double = __pytra_float(__tuple_8(2))
                    val __tuple_9 = __pytra_as_list(reflect(dx, dy, dz, nx, ny, nz))
                    var rdx: Double = __pytra_float(__tuple_9(0))
                    var rdy: Double = __pytra_float(__tuple_9(1))
                    var rdz: Double = __pytra_float(__tuple_9(2))
                    val __tuple_10 = __pytra_as_list(refract(dx, dy, dz, nx, ny, nz, 1.0 / 1.45))
                    var tdx: Double = __pytra_float(__tuple_10(0))
                    var tdy: Double = __pytra_float(__tuple_10(1))
                    var tdz: Double = __pytra_float(__tuple_10(2))
                    val __tuple_11 = __pytra_as_list(sky_color(rdx, rdy, rdz, tphase))
                    var sr: Double = __pytra_float(__tuple_11(0))
                    var sg: Double = __pytra_float(__tuple_11(1))
                    var sb: Double = __pytra_float(__tuple_11(2))
                    val __tuple_12 = __pytra_as_list(sky_color(tdx, tdy, tdz, __pytra_float(tphase) + 0.8))
                    var tr: Double = __pytra_float(__tuple_12(0))
                    var tg: Double = __pytra_float(__tuple_12(1))
                    var tb: Double = __pytra_float(__tuple_12(2))
                    var cosi: Double = __pytra_max((-((dx * nx + dy * ny) + dz * nz)), 0.0)
                    var fr: Double = schlick(cosi, 0.04)
                    r = ((tr * (1.0 - fr)) + sr * fr)
                    g = ((tg * (1.0 - fr)) + sg * fr)
                    b = ((tb * (1.0 - fr)) + sb * fr)
                    lxv = lx - hx
                    lyv = ly - hy
                    lzv = lz - hz
                    val __tuple_13 = __pytra_as_list(normalize(lxv, lyv, lzv))
                    ldx = __pytra_float(__tuple_13(0))
                    ldy = __pytra_float(__tuple_13(1))
                    ldz = __pytra_float(__tuple_13(2))
                    ndotl = __pytra_max(((nx * ldx + ny * ldy) + nz * ldz), 0.0)
                    val __tuple_14 = __pytra_as_list(normalize(ldx - dx, ldy - dy, ldz - dz))
                    var hvx: Double = __pytra_float(__tuple_14(0))
                    var hvy: Double = __pytra_float(__tuple_14(1))
                    var hvz: Double = __pytra_float(__tuple_14(2))
                    var ndoth: Double = __pytra_max(((nx * hvx + ny * hvy) + nz * hvz), 0.0)
                    var spec: Double = ndoth * ndoth
                    spec = spec * spec
                    spec = spec * spec
                    spec = spec * spec
                    glow = (10.0 / ((((1.0 + lxv * lxv) + lyv * lyv) + lzv * lzv)))
                    r += ((0.2 * ndotl + 0.8 * spec) + 0.45 * glow)
                    g += ((0.18 * ndotl + 0.6 * spec) + 0.35 * glow)
                    b += ((0.26 * ndotl + 1.0 * spec) + 0.65 * glow)
                    if (hit_kind == 2L) {
                        r *= 0.95
                        g *= 1.05
                        b *= 1.1
                    } else {
                        if (hit_kind == 3L) {
                            r *= 1.08
                            g *= 0.98
                            b *= 1.04
                        } else {
                            r *= 1.02
                            g *= 1.1
                            b *= 0.95
                        }
                    }
                }
            }
            r = math_native.sqrt(clamp01(r))
            g = math_native.sqrt(clamp01(g))
            b = math_native.sqrt(clamp01(b))
            __pytra_set_index(frame, row_base + px, quantize_332(r, g, b))
            px += 1L
        }
        py += 1L
    }
    return __pytra_bytes(frame)
}

def run_16_glass_sculpture_chaos(): Unit = {
    var width: Long = 320L
    var height: Long = 240L
    var frames_n: Long = 72L
    var out_path: String = "sample/out/16_glass_sculpture_chaos.gif"
    var start: Double = __pytra_perf_counter()
    var frames: mutable.ArrayBuffer[Any] = __pytra_as_list(mutable.ArrayBuffer[Any]())
    var i: Long = 0L
    while (i < frames_n) {
        frames.append(render_frame(width, height, i, frames_n))
        i += 1L
    }
    save_gif(out_path, width, height, frames, palette_332(), 6L, 0L)
    var elapsed: Double = __pytra_perf_counter() - start
    __pytra_print("output:", out_path)
    __pytra_print("frames:", frames_n)
    __pytra_print("elapsed_sec:", elapsed)
}

def main(args: Array[String]): Unit = {
    val _ = run_16_glass_sculpture_chaos()
}
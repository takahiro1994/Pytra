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


// 06: Sample that sweeps Julia-set parameters and outputs a GIF.

def julia_palette(): mutable.ArrayBuffer[Long] = {
    var palette: mutable.ArrayBuffer[Long] = __pytra_bytearray(256L * 3L)
    __pytra_set_index(palette, 0L, 0L)
    __pytra_set_index(palette, 1L, 0L)
    __pytra_set_index(palette, 2L, 0L)
    var i: Long = 1L
    while (i < 256L) {
        var t: Double = ((__pytra_float(i - 1L)) / 254.0)
        var r: Long = __pytra_int(255.0 * ((((9.0 * (1.0 - t)) * t) * t) * t))
        var g: Long = __pytra_int(255.0 * ((((15.0 * (1.0 - t)) * (1.0 - t)) * t) * t))
        var b: Long = __pytra_int(255.0 * ((((8.5 * (1.0 - t)) * (1.0 - t)) * (1.0 - t)) * t))
        __pytra_set_index(palette, (i * 3L + 0L), r)
        __pytra_set_index(palette, (i * 3L + 1L), g)
        __pytra_set_index(palette, (i * 3L + 2L), b)
        i += 1L
    }
    return __pytra_bytes(palette)
}

def render_frame(width: Long, height: Long, cr: Double, ci: Double, max_iter: Long, phase: Long): mutable.ArrayBuffer[Long] = {
    var frame: mutable.ArrayBuffer[Long] = __pytra_bytearray(width * height)
    var y: Long = 0L
    while (y < height) {
        var row_base: Long = y * width
        var zy0: Double = ((-1.2) + (2.4 * ((__pytra_float(y) / (__pytra_float(height - 1L))))))
        var x: Long = 0L
        while (x < width) {
            var zx: Double = ((-1.8) + (3.6 * ((__pytra_float(x) / (__pytra_float(width - 1L))))))
            var zy: Double = zy0
            var i: Long = 0L
            boundary:
                given __breakLabel_2: boundary.Label[Unit] = summon[boundary.Label[Unit]]
                while (i < max_iter) {
                    boundary:
                        given __continueLabel_3: boundary.Label[Unit] = summon[boundary.Label[Unit]]
                        var zx2: Double = zx * zx
                        var zy2: Double = zy * zy
                        if (zx2 + zy2 > 4.0) {
                            break(())(using __breakLabel_2)
                        }
                        zy = ((2.0 * zx * zy) + ci)
                        zx = (zx2 - zy2 + cr)
                        i += 1L
                }
            if (i >= max_iter) {
                __pytra_set_index(frame, row_base + x, 0L)
            } else {
                var color_index: Long = (1L + (((__pytra_int(i * 224L / max_iter) + phase)) % 255L))
                __pytra_set_index(frame, row_base + x, color_index)
            }
            x += 1L
        }
        y += 1L
    }
    return __pytra_bytes(frame)
}

def run_06_julia_parameter_sweep(): Unit = {
    var width: Long = 320L
    var height: Long = 240L
    var frames_n: Long = 72L
    var max_iter: Long = 180L
    var out_path: String = "sample/out/06_julia_parameter_sweep.gif"
    var start: Double = __pytra_perf_counter()
    var frames: mutable.ArrayBuffer[Any] = __pytra_as_list(mutable.ArrayBuffer[Any]())
    var center_cr: Double = __pytra_float(-0.745)
    var center_ci: Double = 0.186
    var radius_cr: Double = 0.12
    var radius_ci: Double = 0.1
    var start_offset: Long = 20L
    var phase_offset: Long = 180L
    var i: Long = 0L
    while (i < frames_n) {
        var t: Double = (__pytra_float((i + start_offset) % frames_n) / __pytra_float(frames_n))
        var angle: Double = (2.0 * math_native.pi * t)
        var cr: Double = (center_cr + radius_cr * math_native.cos(angle))
        var ci: Double = (center_ci + radius_ci * math_native.sin(angle))
        var phase: Long = (((phase_offset + i * 5L)) % 255L)
        frames.append(render_frame(width, height, cr, ci, max_iter, phase))
        i += 1L
    }
    save_gif(out_path, width, height, frames, julia_palette(), 8L, 0L)
    var elapsed: Double = __pytra_perf_counter() - start
    __pytra_print("output:", out_path)
    __pytra_print("frames:", frames_n)
    __pytra_print("elapsed_sec:", elapsed)
}

def main(args: Array[String]): Unit = {
    val _ = run_06_julia_parameter_sweep()
}
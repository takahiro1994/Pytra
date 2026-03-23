import java.nio.file.{Files, Paths}
import scala.collection.mutable
import scala.util.boundary, boundary.break

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


// 09: Sample that outputs a simple fire effect as a GIF.

def fire_palette(): mutable.ArrayBuffer[Long] = {
    var p: mutable.ArrayBuffer[Long] = mutable.ArrayBuffer[Long]()
    var i: Long = 0L
    while (i < 256L) {
        var r: Long = 0L
        var g: Long = 0L
        var b: Long = 0L
        if (i < 85L) {
            r = i * 3L
            g = 0L
            b = 0L
        } else {
            if (i < 170L) {
                r = 255L
                g = ((i - 85L) * 3L)
                b = 0L
            } else {
                r = 255L
                g = 255L
                b = ((i - 170L) * 3L)
            }
        }
        p.append(r)
        p.append(g)
        p.append(b)
        i += 1L
    }
    return __pytra_bytes(p)
}

def run_09_fire_simulation(): Unit = {
    var w: Long = 380L
    var h: Long = 260L
    var steps: Long = 420L
    var out_path: String = "sample/out/09_fire_simulation.gif"
    var start: Double = __pytra_perf_counter()
    var heat: mutable.ArrayBuffer[Any] = __pytra_as_list(mutable.ArrayBuffer[Any]())
    var i: Long = 0L
    while (i < h) {
        heat.append(__pytra_list_repeat(0L, w))
        i += 1L
    }
    var frames: mutable.ArrayBuffer[Any] = __pytra_as_list(mutable.ArrayBuffer[Any]())
    var t: Long = 0L
    while (t < steps) {
        var x: Long = 0L
        x = 0L
        while (x < w) {
            var py_val: Long = (170L + (((x * 13L + t * 17L)) % 86L))
            __pytra_set_index(__pytra_as_list(__pytra_get_index(heat, h - 1L)).asInstanceOf[mutable.ArrayBuffer[Long]], x, py_val)
            x += 1L
        }
        var y: Long = 1L
        while (y < h) {
            x = 0L
            while (x < w) {
                var a: Long = __pytra_int(__pytra_get_index(__pytra_as_list(__pytra_get_index(heat, y)).asInstanceOf[mutable.ArrayBuffer[Long]], x))
                var b: Long = __pytra_int(__pytra_get_index(__pytra_as_list(__pytra_get_index(heat, y)).asInstanceOf[mutable.ArrayBuffer[Long]], (((x - 1L + w)) % w)))
                var c: Long = __pytra_int(__pytra_get_index(__pytra_as_list(__pytra_get_index(heat, y)).asInstanceOf[mutable.ArrayBuffer[Long]], ((x + 1L) % w)))
                var d: Long = __pytra_int(__pytra_get_index(__pytra_as_list(__pytra_get_index(heat, ((y + 1L) % h))).asInstanceOf[mutable.ArrayBuffer[Long]], x))
                var v: Long = __pytra_int(((a + b + c) + d) / 4L)
                var cool: Long = (1L + (((x + y + t)) % 3L))
                var nv: Long = v - cool
                __pytra_set_index(__pytra_as_list(__pytra_get_index(heat, y - 1L)).asInstanceOf[mutable.ArrayBuffer[Long]], x, __pytra_ifexp((nv > 0L), nv, 0L))
                x += 1L
            }
            y += 1L
        }
        var frame: mutable.ArrayBuffer[Long] = __pytra_bytearray(w * h)
        var yy: Long = 0L
        while (yy < h) {
            var row_base: Long = yy * w
            var xx: Long = 0L
            while (xx < w) {
                __pytra_set_index(frame, row_base + xx, __pytra_int(__pytra_get_index(__pytra_as_list(__pytra_get_index(heat, yy)).asInstanceOf[mutable.ArrayBuffer[Long]], xx)))
                xx += 1L
            }
            yy += 1L
        }
        frames.append(__pytra_bytes(frame))
        t += 1L
    }
    save_gif(out_path, w, h, frames, fire_palette(), 4L, 0L)
    var elapsed: Double = __pytra_perf_counter() - start
    __pytra_print("output:", out_path)
    __pytra_print("frames:", steps)
    __pytra_print("elapsed_sec:", elapsed)
}

def main(args: Array[String]): Unit = {
    val _ = run_09_fire_simulation()
}
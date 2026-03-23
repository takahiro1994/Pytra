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


// 12: Sample that outputs intermediate states of bubble sort as a GIF.

def render(values: mutable.ArrayBuffer[Long], w: Long, h: Long): mutable.ArrayBuffer[Long] = {
    var frame: mutable.ArrayBuffer[Long] = __pytra_bytearray(w * h)
    var n: Long = __pytra_len(values)
    var bar_w: Double = __pytra_float(w) / __pytra_float(n)
    var i: Long = 0L
    while (i < n) {
        var x0: Long = __pytra_int(__pytra_float(i) * bar_w)
        var x1: Long = __pytra_int((__pytra_float(i + 1L)) * bar_w)
        if (x1 <= x0) {
            x1 = x0 + 1L
        }
        var bh: Long = __pytra_int((__pytra_float(__pytra_int(__pytra_get_index(values, i))) / __pytra_float(n)) * __pytra_float(h))
        var y: Long = h - bh
        y = y
        while (y < h) {
            var x: Long = x0
            while (x < x1) {
                __pytra_set_index(frame, (y * w + x), 255L)
                x += 1L
            }
            y += 1L
        }
        i += 1L
    }
    return __pytra_bytes(frame)
}

def run_12_sort_visualizer(): Unit = {
    var w: Long = 320L
    var h: Long = 180L
    var n: Long = 124L
    var out_path: String = "sample/out/12_sort_visualizer.gif"
    var start: Double = __pytra_perf_counter()
    var values: mutable.ArrayBuffer[Long] = __pytra_as_list(mutable.ArrayBuffer[Long]()).asInstanceOf[mutable.ArrayBuffer[Long]]
    var i: Long = 0L
    i = 0L
    while (i < n) {
        values.append((((i * 37L + 19L)) % n))
        i += 1L
    }
    var frames: mutable.ArrayBuffer[Any] = __pytra_as_list(mutable.ArrayBuffer[Any](render(values, w, h)))
    var frame_stride: Long = 16L
    var op: Long = 0L
    i = 0L
    boundary:
        given __breakLabel_2: boundary.Label[Unit] = summon[boundary.Label[Unit]]
        while (i < n) {
            boundary:
                given __continueLabel_3: boundary.Label[Unit] = summon[boundary.Label[Unit]]
                var swapped: Boolean = false
                var j: Long = 0L
                while (j < (n - i - 1L)) {
                    if (__pytra_int(__pytra_get_index(values, j)) > __pytra_int(__pytra_get_index(values, j + 1L))) {
                        var __swap_tmp_0: Long = __pytra_int(__pytra_get_index(values, j))
                        __pytra_set_index(values, j, __pytra_int(__pytra_get_index(values, j + 1L)))
                        __pytra_set_index(values, j + 1L, __swap_tmp_0)
                        swapped = true
                    }
                    if (op % frame_stride == 0L) {
                        frames.append(render(values, w, h))
                    }
                    op += 1L
                    j += 1L
                }
                if (!swapped) {
                    break(())(using __breakLabel_2)
                }
            i += 1L
        }
    save_gif(out_path, w, h, frames, grayscale_palette(), 3L, 0L)
    var elapsed: Double = __pytra_perf_counter() - start
    __pytra_print("output:", out_path)
    __pytra_print("frames:", __pytra_len(frames))
    __pytra_print("elapsed_sec:", elapsed)
}

def main(args: Array[String]): Unit = {
    val _ = run_12_sort_visualizer()
}
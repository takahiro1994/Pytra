function _png_append_list(dst, src)
    append!(dst, src)
    return nothing
end

function _crc32(data)
    crc = 0xFFFFFFFF
    poly = 0xEDB88320
    for b in data
        crc = xor(crc, Int(b))
        i = 0
        while i < 8
            lowbit = crc & 1
            if lowbit != 0
                crc = xor(crc >> 1, poly)
            else
                crc = crc >> 1
            end
            i += 1
        end
    end
    return xor(crc, 0xFFFFFFFF)
end

function _adler32(data)
    mod = 65521
    s1 = 1
    s2 = 0
    for b in data
        s1 += Int(b)
        if s1 >= mod
            s1 -= mod
        end
        s2 += s1
        s2 = s2 % mod
    end
    return ((s2 << 16) | s1) & 0xFFFFFFFF
end

function _png_u16le(v)
    return UInt8[UInt8(v & 0xFF), UInt8((v >> 8) & 0xFF)]
end

function _png_u32be(v)
    return UInt8[
        UInt8((v >> 24) & 0xFF),
        UInt8((v >> 16) & 0xFF),
        UInt8((v >> 8) & 0xFF),
        UInt8(v & 0xFF),
    ]
end

function _zlib_deflate_store(data)
    out = UInt8[0x78, 0x01]
    n = length(data)
    pos = 1
    while pos <= n
        remain = n - pos + 1
        chunk_len = remain > 65535 ? 65535 : remain
        final = (pos + chunk_len - 1) >= n ? 1 : 0
        push!(out, UInt8(final))
        _png_append_list(out, _png_u16le(chunk_len))
        _png_append_list(out, _png_u16le(xor(0xFFFF, chunk_len)))
        _png_append_list(out, data[pos:(pos + chunk_len - 1)])
        pos += chunk_len
    end
    _png_append_list(out, _png_u32be(_adler32(data)))
    return out
end

function _chunk(chunk_type, data)
    crc_input = UInt8[]
    _png_append_list(crc_input, chunk_type)
    _png_append_list(crc_input, data)
    crc = _crc32(crc_input) & 0xFFFFFFFF
    out = UInt8[]
    _png_append_list(out, _png_u32be(length(data)))
    _png_append_list(out, chunk_type)
    _png_append_list(out, data)
    _png_append_list(out, _png_u32be(crc))
    return out
end

function write_rgb_png(path, width, height, pixels)
    raw = UInt8.(pixels)
    expected = width * height * 3
    if length(raw) != expected
        throw(__pytra_value_error("pixels length mismatch: got=" * string(length(raw)) * " expected=" * string(expected)))
    end

    scanlines = UInt8[]
    row_bytes = width * 3
    y = 0
    while y < height
        push!(scanlines, 0x00)
        start_idx = y * row_bytes + 1
        end_idx = start_idx + row_bytes - 1
        _png_append_list(scanlines, raw[start_idx:end_idx])
        y += 1
    end

    ihdr = UInt8[]
    _png_append_list(ihdr, _png_u32be(width))
    _png_append_list(ihdr, _png_u32be(height))
    _png_append_list(ihdr, UInt8[8, 2, 0, 0, 0])
    idat = _zlib_deflate_store(scanlines)

    png = UInt8[]
    _png_append_list(png, UInt8[137, 80, 78, 71, 13, 10, 26, 10])
    _png_append_list(png, _chunk(UInt8[73, 72, 68, 82], ihdr))
    _png_append_list(png, _chunk(UInt8[73, 68, 65, 84], idat))
    _png_append_list(png, _chunk(UInt8[73, 69, 78, 68], UInt8[]))
    write(path, png)
    return nothing
end

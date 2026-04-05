# gif.ps1 — generated from src/pytra/utils/gif.py via PS1 emitter
# Source: src/runtime/east/utils/gif.east
# DO NOT hand-edit the encoding functions (_gif_append, _gif_u16le, _lzw_encode,
# grayscale_palette).  They are transpiled from the canonical Python source.
# The save_gif I/O adapter uses FileStream to avoid accumulating large GIFs in
# memory; this is an allowed native I/O optimization per the emitter guide §6.

function _gif_append {
    param($dst, $src)
    [void]($dst.AddRange([object[]]@($src)))
}

function _gif_u16le {
    param($v)
    return ,((__pytra_bytearray (__pytra_mklist ($v -band 255) (($v -shr 8) -band 255))))
}

function _lzw_encode {
    param($data_, $min_code_size = 8)
    if (((__pytra_len $data_) -eq 0)) {
        $empty = (__pytra_bytearray 0)
        return ,((__pytra_bytes $empty))
    }
    $clear_code = (1 -shl $min_code_size)
    $end_code = ($clear_code + 1)
    $code_size = ($min_code_size + 1)
    $out = (__pytra_bytearray 0)
    $bit_buffer = 0
    $bit_count = 0
    $bit_buffer = ($bit_buffer -bor ($clear_code -shl $bit_count))
    $bit_count += $code_size
    while (($bit_count -ge 8)) {
        [void]($out.Add(($bit_buffer -band 255)))
        $bit_buffer = ($bit_buffer -shr 8)
        $bit_count -= 8
    }
    $code_size = ($min_code_size + 1)
    foreach ($v in $data_) {
        $bit_buffer = ($bit_buffer -bor ($v -shl $bit_count))
        $bit_count += $code_size
        while (($bit_count -ge 8)) {
            [void]($out.Add(($bit_buffer -band 255)))
            $bit_buffer = ($bit_buffer -shr 8)
            $bit_count -= 8
        }
        $bit_buffer = ($bit_buffer -bor ($clear_code -shl $bit_count))
        $bit_count += $code_size
        while (($bit_count -ge 8)) {
            [void]($out.Add(($bit_buffer -band 255)))
            $bit_buffer = ($bit_buffer -shr 8)
            $bit_count -= 8
        }
        $code_size = ($min_code_size + 1)
    }
    $bit_buffer = ($bit_buffer -bor ($end_code -shl $bit_count))
    $bit_count += $code_size
    while (($bit_count -ge 8)) {
        [void]($out.Add(($bit_buffer -band 255)))
        $bit_buffer = ($bit_buffer -shr 8)
        $bit_count -= 8
    }
    if (($bit_count -gt 0)) {
        [void]($out.Add(($bit_buffer -band 255)))
    }
    return ,((__pytra_bytes $out))
}

function grayscale_palette {
    param()
    $p = (__pytra_bytearray 0)
    $i = 0
    while (($i -lt 256)) {
        [void]($p.Add($i))
        [void]($p.Add($i))
        [void]($p.Add($i))
        $i += 1
    }
    return ,((__pytra_bytes $p))
}

function save_gif {
    param($path, $width, $height, $frames, $palette, $delay_cs = 4, $loop = 0)
    if (((__pytra_len $palette) -ne (256 * 3))) {
        $script:__pytra_exc_type = "ValueError"
        throw "palette must be 256*3 bytes"
    }

    # Convert palette to byte[] for FileStream.Write
    $pal_n = (__pytra_len $palette)
    $pal_bytes = [byte[]]::new($pal_n)
    $pi = 0
    foreach ($pv in $palette) { $pal_bytes[$pi] = [byte]$pv; $pi++ }

    $w_lo = [byte]($width   -band 255); $w_hi = [byte](($width   -shr 8) -band 255)
    $h_lo = [byte]($height  -band 255); $h_hi = [byte](($height  -shr 8) -band 255)
    $d_lo = [byte]($delay_cs -band 255); $d_hi = [byte](($delay_cs -shr 8) -band 255)
    $loop_lo = [byte]($loop -band 255); $loop_hi = [byte](($loop -shr 8) -band 255)

    # Stream directly to file — avoids accumulating 60+ MB in memory
    $fs = [System.IO.File]::Open($path, [System.IO.FileMode]::Create)
    try {
        # GIF89a signature + logical screen descriptor
        $fs.Write([byte[]](71, 73, 70, 56, 57, 97), 0, 6)
        $fs.WriteByte($w_lo); $fs.WriteByte($w_hi)
        $fs.WriteByte($h_lo); $fs.WriteByte($h_hi)
        $fs.WriteByte(247)   # packed field: GCT present, 8-bit colour, GCT size=256
        $fs.WriteByte(0)     # background color index
        $fs.WriteByte(0)     # pixel aspect ratio
        $fs.Write($pal_bytes, 0, $pal_bytes.Length)

        # Netscape Application Extension (animation loop count)
        $fs.Write([byte[]](33, 255, 11, 78, 69, 84, 83, 67, 65, 80, 69, 50, 46, 48, 3, 1), 0, 16)
        $fs.WriteByte($loop_lo); $fs.WriteByte($loop_hi)
        $fs.WriteByte(0)  # block terminator

        foreach ($fr in $frames) {
            $fr_arr = if ($fr -is [array]) { [object[]]$fr } else { [object[]]@($fr) }
            if ($fr_arr.Length -ne ($width * $height)) {
                $script:__pytra_exc_type = "ValueError"
                throw "frame size mismatch"
            }

            # Graphic Control Extension
            $fs.Write([byte[]](33, 249, 4, 0), 0, 4)
            $fs.WriteByte($d_lo); $fs.WriteByte($d_hi)
            $fs.WriteByte(0); $fs.WriteByte(0)

            # Image Descriptor
            $fs.WriteByte(44)                           # ','
            $fs.WriteByte(0); $fs.WriteByte(0)          # left
            $fs.WriteByte(0); $fs.WriteByte(0)          # top
            $fs.WriteByte($w_lo); $fs.WriteByte($w_hi)  # width
            $fs.WriteByte($h_lo); $fs.WriteByte($h_hi)  # height
            $fs.WriteByte(0)                            # no local color table
            $fs.WriteByte(8)                            # LZW minimum code size

            # LZW encode using transpiled PS1 implementation (from gif.py via emitter)
            $compressed = _lzw_encode $fr_arr 8

            # Write LZW data as GIF sub-blocks (max 255 bytes each).
            # Convert to byte[] once for batch $fs.Write() — avoids per-byte WriteByte overhead.
            $compressed_b = [byte[]]$compressed
            $pos = 0
            $clen = $compressed_b.Length
            while ($pos -lt $clen) {
                $chunk_len = [Math]::Min(255, $clen - $pos)
                $fs.WriteByte([byte]$chunk_len)
                $fs.Write($compressed_b, $pos, $chunk_len)
                $pos += $chunk_len
            }
            $fs.WriteByte(0)  # block terminator
        }

        $fs.WriteByte(59)  # GIF Trailer ';'
    } finally {
        $fs.Close()
    }
}

#Requires -Version 5.1

$pytra_runtime = Join-Path $PSScriptRoot "built_in/py_runtime.ps1"
if (Test-Path $pytra_runtime) { . $pytra_runtime }

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

# PNG 書き出しユーティリティ（Python実行用）。

function _png_append {
    param($dst, $src)
    [void]($dst.AddRange([object[]]@($src)))
}

function _crc32 {
    param($data_)
    $crc = 4294967295
    $poly = 3988292384
    foreach ($b in $data_) {
        $crc = ($crc -bxor $b)
        $i = 0
        while (($i -lt 8)) {
            $lowbit = ($crc -band 1)
            if (($lowbit -ne 0)) {
                $crc = (($crc -shr 1) -bxor $poly)
            } else {
                $crc = ($crc -shr 1)
            }
            $i += 1
        }
    }
    return ,(($crc -bxor 4294967295))
}

function _adler32 {
    param($data_)
    $mod = 65521
    $s1 = 1
    $s2 = 0
    foreach ($b in $data_) {
        $s1 += $b
        if (($s1 -ge $mod)) {
            $s1 -= $mod
        }
        $s2 += $s1
        $s2 = ($s2 % $mod)
    }
    return ,(((($s2 -shl 16) -bor $s1) -band 4294967295))
}

function _png_u16le {
    param($v)
    return ,((__pytra_bytearray ([System.Collections.Generic.List[object]]@(($v -band 255), (($v -shr 8) -band 255)))))
}

function _png_u32be {
    param($v)
    return ,((__pytra_bytearray ([System.Collections.Generic.List[object]]@((($v -shr 24) -band 255), (($v -shr 16) -band 255), (($v -shr 8) -band 255), ($v -band 255)))))
}

function _zlib_deflate_store {
    param($data_)
    $out = (__pytra_bytearray 0)
    [void]((_png_append $out (__pytra_bytearray ([System.Collections.Generic.List[object]]@(120, 1)))))
    $n = (__pytra_len $data_)
    $pos = 0
    while (($pos -lt $n)) {
        $remain = ($n - $pos)
        $chunk_len = $(if (($remain -gt 65535)) { 65535 } else { $remain })
        $final = $(if ((($pos + $chunk_len) -ge $n)) { 1 } else { 0 })
        [void]($out.Add($final))
        [void]((_png_append $out (_png_u16le $chunk_len)))
        [void]((_png_append $out (_png_u16le (65535 -bxor $chunk_len))))
        [void]($out.AddRange([object[]]@((__pytra_str_slice $data_ $pos ($pos + $chunk_len)))))
        $pos += $chunk_len
    }
    [void]((_png_append $out (_png_u32be (_adler32 $data_))))
    return ,($out)
}

function _chunk {
    param($chunk_type, $data_)
    $crc_input = (__pytra_bytearray 0)
    [void]((_png_append $crc_input $chunk_type))
    [void]((_png_append $crc_input $data_))
    $crc = ((_crc32 $crc_input) -band 4294967295)
    $out = (__pytra_bytearray 0)
    [void]((_png_append $out (_png_u32be (__pytra_len $data_))))
    [void]((_png_append $out $chunk_type))
    [void]((_png_append $out $data_))
    [void]((_png_append $out (_png_u32be $crc)))
    return ,($out)
}

function write_rgb_png {
    param($path, $width, $height, $pixels)
    $raw = (__pytra_bytearray 0)
    [void]($raw.AddRange([object[]]@($pixels)))
    $expected = (($width * $height) * 3)
    if (((__pytra_len $raw) -ne $expected)) {
        $script:__pytra_exc_type = "ValueError"
        throw ((("pixels length mismatch: got=" + (__pytra_str (__pytra_len $raw))) + " expected=") + (__pytra_str $expected))
    }
    $scanlines = (__pytra_bytearray 0)
    $row_bytes = ($width * 3)
    $y = 0
    while (($y -lt $height)) {
        [void]($scanlines.Add(0))
        $start = ($y * $row_bytes)
        [void]($scanlines.AddRange([object[]]@((__pytra_str_slice $raw $start ($start + $row_bytes)))))
        $y += 1
    }
    $ihdr = (__pytra_bytearray 0)
    [void]((_png_append $ihdr (_png_u32be $width)))
    [void]((_png_append $ihdr (_png_u32be $height)))
    [void]((_png_append $ihdr (__pytra_bytearray ([System.Collections.Generic.List[object]]@(8, 2, 0, 0, 0)))))
    $idat = (_zlib_deflate_store $scanlines)
    $png = (__pytra_bytearray 0)
    [void]((_png_append $png (__pytra_bytearray ([System.Collections.Generic.List[object]]@(137, 80, 78, 71, 13, 10, 26, 10)))))
    [void]((_png_append $png (_chunk (__pytra_bytearray ([System.Collections.Generic.List[object]]@(73, 72, 68, 82))) $ihdr)))
    [void]((_png_append $png (_chunk (__pytra_bytearray ([System.Collections.Generic.List[object]]@(73, 68, 65, 84))) $idat)))
    $iend_data = (__pytra_bytearray 0)
    [void]((_png_append $png (_chunk (__pytra_bytearray ([System.Collections.Generic.List[object]]@(73, 69, 78, 68))) $iend_data)))
    $f = (__pytra_open $path "wb")
    try {
        [void]((__pytra_file_write $f (__pytra_bytes $png)))
    } finally {
        [void]($f.Close())
    }
}

# re_native.ps1 — native seam for pytra.std.re

function __native_re_sub {
    param($pattern, $repl, $text, $count = 0)
    if ($count -eq 0) {
        return [regex]::Replace($text, $pattern, $repl)
    }
    $rx = [regex]$pattern
    $n = 0
    return $rx.Replace($text, { param($m) if ($n -lt $count) { $n++; $repl } else { $m.Value } })
}

function __native_re_match {
    param($pattern, $text)
    $m = [regex]::Match($text, "^" + $pattern)
    if ($m.Success) { return $m.Value } else { return $null }
}

function __native_re_search {
    param($pattern, $text)
    $m = [regex]::Match($text, $pattern)
    if ($m.Success) { return $m.Value } else { return $null }
}

function __native_re_findall {
    param($pattern, $text)
    $result = ([System.Collections.Generic.List[object]]::new())
    foreach ($m in [regex]::Matches($text, $pattern)) { [void]$result.Add($m.Value) }
    return ,$result
}

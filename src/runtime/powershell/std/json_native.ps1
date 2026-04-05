# json_native.ps1 — native seam for pytra.std.json

function __pytra_json_dumps_value {
    param($obj, $indent, $level)
    if ($null -eq $obj) { return "null" }
    if ($obj -is [bool]) { if ($obj) { return "true" } else { return "false" } }
    if ($obj -is [string]) {
        $s = $obj.Replace('\', '\\').Replace('"', '\"').Replace("`n", '\n').Replace("`r", '\r').Replace("`t", '\t')
        return '"' + $s + '"'
    }
    if ($obj -is [System.Collections.IList] -or $obj -is [array]) {
        $arr = @($obj)
        if ($arr.Count -eq 0) { return "[]" }
        if ($null -eq $indent) {
            $parts = @(); foreach ($item in $arr) { $parts += (__pytra_json_dumps_value $item $null 0) }
            return "[" + ($parts -join ", ") + "]"
        }
        $pad = " " * ($indent * ($level + 1))
        $closePad = " " * ($indent * $level)
        $inner = @(); foreach ($item in $arr) { $inner += ($pad + (__pytra_json_dumps_value $item $indent ($level + 1))) }
        return ("[`n" + ($inner -join (",`n")) + "`n" + $closePad + "]")
    }
    if ($obj -is [System.Collections.IDictionary]) {
        $keys = @($obj.Keys)
        if ($keys.Count -eq 0) { return "{}" }
        if ($null -eq $indent) {
            $parts = @()
            foreach ($key in $keys) { $parts += ('"' + [string]$key + '": ' + (__pytra_json_dumps_value $obj[$key] $null 0)) }
            return "{" + ($parts -join ", ") + "}"
        }
        $pad = " " * ($indent * ($level + 1))
        $closePad = " " * ($indent * $level)
        $inner = @()
        foreach ($key in $keys) { $inner += ($pad + '"' + [string]$key + '": ' + (__pytra_json_dumps_value $obj[$key] $indent ($level + 1))) }
        return ("{`n" + ($inner -join (",`n")) + "`n" + $closePad + "}")
    }
    return [string]$obj
}

function __pytra_json_dumps {
    param($obj, $ensure_ascii = $true, $indent = $null, $separators = $null)
    return (__pytra_json_dumps_value $obj $indent 0)
}

function __pytra_json_loads {
    param($text)
    try {
        $parsed = ConvertFrom-Json $text -ErrorAction Stop
        $result = @{}
        $result["__type__"] = "JsonValue"
        $result["raw"] = $parsed
        return $result
    } catch { return $null }
}

function JsonValue_as_str {
    param($self)
    $raw = $self["raw"]
    if ($raw -is [string]) { return $raw }
    return $null
}

function JsonValue_as_int {
    param($self)
    $raw = $self["raw"]
    if ($raw -is [int] -or $raw -is [long]) { return [long]$raw }
    return $null
}

function JsonValue_as_float {
    param($self)
    $raw = $self["raw"]
    if ($raw -is [double] -or $raw -is [float] -or $raw -is [decimal]) { return [double]$raw }
    return $null
}

function JsonValue_as_bool {
    param($self)
    $raw = $self["raw"]
    if ($raw -is [bool]) { return $raw }
    return $null
}

function JsonValue_as_obj {
    param($self)
    $raw = $self["raw"]
    if ($raw -is [hashtable] -or $raw -is [System.Collections.IDictionary]) {
        $result = @{}; $result["__type__"] = "JsonObj"; $result["raw"] = $raw; return $result
    }
    if ($null -ne $raw -and $raw.GetType().Name -eq "PSCustomObject") {
        $ht = @{}; foreach ($prop in $raw.PSObject.Properties) { $ht[$prop.Name] = $prop.Value }
        $result = @{}; $result["__type__"] = "JsonObj"; $result["raw"] = $ht; return $result
    }
    return $null
}

function JsonValue_as_arr {
    param($self)
    $raw = $self["raw"]
    if ($raw -is [array] -or $raw -is [System.Collections.IList]) {
        $result = @{}; $result["__type__"] = "JsonArr"; $result["raw"] = $raw; return $result
    }
    return $null
}

function __pytra_json_loads_arr {
    param($text)
    try {
        $parsed = ConvertFrom-Json $text -ErrorAction Stop
        if ($parsed -is [System.Array] -or $parsed -is [System.Collections.IList]) {
            $result = @{}
            $result["__type__"] = "JsonArr"
            $result["raw"] = $parsed
            return $result
        }
        return $null
    } catch { return $null }
}

# argparse_native.ps1 — native seam for pytra.std.argparse.ArgumentParser

function ArgumentParser {
    param($self, $prog = "")
    if ($null -eq $self) { $self = @{} }
    $self["__type__"] = "ArgumentParser"
    $self["_prog"] = $prog
    $self["_args"] = ([System.Collections.Generic.List[object]]::new())
}

function ArgumentParser_add_argument {
    param($self, $name_or_flag, $long_flag = $null, $choices = $null, $default = $null, $action = $null)
    # Emitter limitation: keyword-only args get positionally placed after positional args.
    # Detect if $long_flag is actually an action value (e.g. add_argument("--flag", action="store_true"))
    $__known_actions = @("store_true", "store_false", "append", "count")
    if ($null -ne $long_flag -and $__known_actions -contains $long_flag -and $action -eq $null) {
        $action = $long_flag
        $long_flag = $null
    }
    $spec = @{}
    $spec["name_or_flag"] = $name_or_flag
    $spec["long_flag"] = $long_flag
    $spec["choices"] = $choices
    $spec["default"] = $default
    $spec["action"] = $action
    # Determine dest key
    if ($name_or_flag.StartsWith("-")) {
        $dest = if ($null -ne $long_flag) { $long_flag.TrimStart("-").Replace("-", "_") } else { $name_or_flag.TrimStart("-").Replace("-", "_") }
    } else {
        $dest = $name_or_flag
    }
    $spec["dest"] = $dest
    [void]$self["_args"].Add($spec)
}

function ArgumentParser_parse_args {
    param($self, $argv_list)
    $result = @{}
    # Initialize defaults
    foreach ($spec in $self["_args"]) {
        $dest = $spec["dest"]
        if ($spec["action"] -eq "store_true") {
            $result[$dest] = $false
        } elseif ($null -ne $spec["default"]) {
            $result[$dest] = $spec["default"]
        } else {
            $result[$dest] = $null
        }
    }
    $i = 0
    $pos_args = @($self["_args"] | Where-Object { -not $_["name_or_flag"].StartsWith("-") })
    $pos_idx = 0
    while ($i -lt $argv_list.Count) {
        $tok = [string]$argv_list[$i]
        if ($tok.StartsWith("-")) {
            $matched = $null
            foreach ($spec in $self["_args"]) {
                if ($spec["name_or_flag"] -eq $tok -or $spec["long_flag"] -eq $tok) {
                    $matched = $spec; break
                }
            }
            if ($null -ne $matched) {
                if ($matched["action"] -eq "store_true") {
                    $result[$matched["dest"]] = $true
                } else {
                    $i++
                    if ($i -lt $argv_list.Count) { $result[$matched["dest"]] = [string]$argv_list[$i] }
                }
            }
        } else {
            if ($pos_idx -lt $pos_args.Count) {
                $result[$pos_args[$pos_idx]["dest"]] = $tok
                $pos_idx++
            }
        }
        $i++
    }
    return $result
}

#Requires -Version 5.1

$pytra_runtime = Join-Path $PSScriptRoot "py_runtime.ps1"
if (Test-Path $pytra_runtime) { . $pytra_runtime }

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

# import: pytra.std.time

# import: pytra.utils.gif

function next_state {
    param()
    $nxt = @()
    for ($_i = $null; $true; ) {
        $row = @()
        for ($_i = $null; $true; ) {
            $cnt = 0
            for ($_i = $null; $true; ) {
                for ($_i = $null; $true; ) {
                    if ((($dx -ne 0) -or ($dy -ne 0))) {
                        $nx = ((($x + $dx) + $w) % $w)
                        $ny = ((($y + $dy) + $h) % $h)
                        $cnt += $grid[$ny][$nx]
                    }
                }
            }
            $alive = $grid[$y][$x]
            if ((($alive -eq 1) -and (($cnt -eq 2) -or ($cnt -eq 3)))) {
                $row += @(1)
            } elseif ((($alive -eq 0) -and ($cnt -eq 3))) {
                $row += @(1)
            } else {
                $row += @(0)
            }
        }
        $nxt += @($row)
    }
    return $nxt
}

function render {
    param()
    $width = ($w * $cell)
    $height = ($h * $cell)
    $frame = bytearray ($width * $height)
    for ($_i = $null; $true; ) {
        for ($_i = $null; $true; ) {
            $v = $(if ($grid[$y][$x]) { 255 } else { 0 })
            for ($_i = $null; $true; ) {
                $base = (((($y * $cell) + $yy) * $width) + ($x * $cell))
                for ($_i = $null; $true; ) {
                    $frame[($base + $xx)] = $v
                }
            }
        }
    }
    return bytes $frame
}

function run_07_game_of_life_loop {
    param()
    $w = 144
    $h = 108
    $cell = 4
    $steps = 105
    $out_path = "sample/out/07_game_of_life_loop.gif"
    $start = perf_counter
    $grid = $null
    for ($_i = $null; $true; ) {
        for ($_i = $null; $true; ) {
            $noise = ((((($x * 37) + ($y * 73)) + (($x * $y) % 19)) + (($x + $y) % 11)) % 97)
            if (($noise -lt 3)) {
                $grid[$y][$x] = 1
            }
        }
    }
    $glider = @(@(0, 1, 0), @(0, 0, 1), @(1, 1, 1))
    $r_pentomino = @(@(0, 1, 1), @(1, 1, 0), @(0, 1, 0))
    $lwss = @(@(0, 1, 1, 1, 1), @(1, 0, 0, 0, 1), @(0, 0, 0, 0, 1), @(1, 0, 0, 1, 0))
    for ($_i = $null; $true; ) {
        for ($_i = $null; $true; ) {
            $kind = ((($gx * 7) + ($gy * 11)) % 3)
            if (($kind -eq 0)) {
                $ph = __pytra_len $glider
                for ($_i = $null; $true; ) {
                    $pw = __pytra_len $glider[$py]
                    for ($_i = $null; $true; ) {
                        if (($glider[$py][$px] -eq 1)) {
                            $grid[(($gy + $py) % $h)][(($gx + $px) % $w)] = 1
                        }
                    }
                }
            } elseif (($kind -eq 1)) {
                $ph = __pytra_len $r_pentomino
                for ($_i = $null; $true; ) {
                    $pw = __pytra_len $r_pentomino[$py]
                    for ($_i = $null; $true; ) {
                        if (($r_pentomino[$py][$px] -eq 1)) {
                            $grid[(($gy + $py) % $h)][(($gx + $px) % $w)] = 1
                        }
                    }
                }
            } else {
                $ph = __pytra_len $lwss
                for ($_i = $null; $true; ) {
                    $pw = __pytra_len $lwss[$py]
                    for ($_i = $null; $true; ) {
                        if (($lwss[$py][$px] -eq 1)) {
                            $grid[(($gy + $py) % $h)][(($gx + $px) % $w)] = 1
                        }
                    }
                }
            }
        }
    }
    $frames = @()
    for ($_i = $null; $true; ) {
        $frames += @(render $grid $w $h $cell)
        $grid = next_state $grid $w $h
    }
    save_gif $out_path ($w * $cell) ($h * $cell) $frames grayscale_palette
    $elapsed = (perf_counter - $start)
    __pytra_print "output:" $out_path
    __pytra_print "frames:" $steps
    __pytra_print "elapsed_sec:" $elapsed
}

if (Get-Command -Name main -ErrorAction SilentlyContinue) {
    main
}

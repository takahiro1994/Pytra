#Requires -Version 5.1

$pytra_runtime = Join-Path $PSScriptRoot "py_runtime.ps1"
if (Test-Path $pytra_runtime) { . $pytra_runtime }

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

# import: pytra.utils.assertions

function calc {
    param($x, $y)
    return (($x - $y) * 2)
}

function div_calc {
    param($x, $y)
    return ($x / $y)
}

function _case_main {
    param()
    __pytra_print (calc 9 4)
    __pytra_print (div_calc 9 4)
}

(_case_main)

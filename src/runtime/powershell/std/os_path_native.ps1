# os_path_native.ps1 — native seam for pytra.std.os_path (os.path)

function __native_join { param($a, $b) return [System.IO.Path]::Combine($a, $b) }
function __native_dirname { param($p) $d = [System.IO.Path]::GetDirectoryName($p); if ($d -eq $null) { return "" }; return $d }
function __native_basename { param($p) return [System.IO.Path]::GetFileName($p) }
function __native_splitext { param($p) $ext = [System.IO.Path]::GetExtension($p); $stem = $p.Substring(0, $p.Length - $ext.Length); return @($stem, $ext) }
function __native_abspath { param($p) return [System.IO.Path]::GetFullPath($p) }
function __native_exists { param($p) return (Test-Path $p) }
function __native_isfile { param($p) return (Test-Path $p -PathType Leaf) }
function __native_isdir { param($p) return (Test-Path $p -PathType Container) }

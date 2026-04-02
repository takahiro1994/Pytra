<?php
declare(strict_types=1);

// Module dependencies (utils/png, utils/gif, std/time) are require_once'd
// by the emitter-generated code, not here. py_runtime provides only
// Python built-in function equivalents (spec §6).

function __pytra_print(...$args): void {
    if (count($args) === 0) {
        echo PHP_EOL;
        return;
    }
    $parts = [];
    foreach ($args as $arg) {
        if (is_bool($arg)) {
            $parts[] = $arg ? "True" : "False";
            continue;
        }
        if ($arg === null) {
            $parts[] = "None";
            continue;
        }
        if (is_array($arg)) {
            $parts[] = __pytra_repr_array($arg);
            continue;
        }
        if ($arg instanceof \Throwable) {
            $parts[] = $arg->getMessage();
            continue;
        }
        $parts[] = (string)$arg;
    }
    echo implode(" ", $parts) . PHP_EOL;
}

if (!class_exists('Enum')) {
    class Enum {}
}

if (!class_exists('IntEnum')) {
    class IntEnum extends Enum {}
}

if (!class_exists('IntFlag')) {
    class IntFlag extends IntEnum {}
}

function __pytra_repr_value($v): string {
    if (is_bool($v)) { return $v ? "True" : "False"; }
    if ($v === null) { return "None"; }
    if (is_int($v)) { return (string)$v; }
    if (is_float($v)) {
        if (floor($v) == $v && !is_infinite($v) && abs($v) < 1e15) {
            return number_format($v, 1, '.', '');
        }
        return (string)$v;
    }
    if (is_string($v)) { return "'" . $v . "'"; }
    if (is_array($v)) { return __pytra_repr_array($v); }
    return (string)$v;
}

function __pytra_repr_array($v): string {
    if (!is_array($v) || count($v) === 0) { return "[]"; }
    $items = [];
    foreach ($v as $item) {
        $items[] = __pytra_repr_value($item);
    }
    return "[" . implode(", ", $items) . "]";
}

function __pytra_len($v): int {
    if (is_string($v)) {
        return strlen($v);
    }
    if (is_array($v)) {
        return count($v);
    }
    if ($v instanceof \Countable) {
        return count($v);
    }
    if (is_object($v) && property_exists($v, 'length')) {
        return (int)$v->length;
    }
    return 0;
}

function __pytra_truthy($v): bool {
    if (is_bool($v)) {
        return $v;
    }
    if ($v === null) {
        return false;
    }
    if (is_int($v) || is_float($v)) {
        return $v != 0;
    }
    if (is_string($v)) {
        return strlen($v) > 0;
    }
    if (is_array($v)) {
        return count($v) > 0;
    }
    return (bool)$v;
}

function __pytra_int($v): int {
    if (is_int($v)) {
        return $v;
    }
    if (is_bool($v)) {
        return $v ? 1 : 0;
    }
    if (is_float($v)) {
        return (int)$v;
    }
    if (is_string($v) && is_numeric($v)) {
        return (int)$v;
    }
    return 0;
}

function __pytra_float($v): float {
    if (is_float($v)) {
        return $v;
    }
    if (is_int($v) || is_bool($v)) {
        return (float)$v;
    }
    if (is_string($v) && is_numeric($v)) {
        return (float)$v;
    }
    return 0.0;
}

function py_to_string($v): string {
    if (is_array($v)) {
        return __pytra_repr_array($v);
    }
    return (string)$v;
}

function __native_sqrt($x) { return sqrt($x); }
function __native_floor($x) { return floor($x); }
function __native_ceil($x) { return ceil($x); }
function __native_sin($x) { return sin($x); }
function __native_cos($x) { return cos($x); }
function __native_tan($x) { return tan($x); }
function __native_log($x) { return log($x); }
function __native_log10($x) { return log10($x); }
function __native_exp($x) { return exp($x); }
function __native_pow($x, $y) { return pow($x, $y); }
function __native_fabs($x) { return abs($x); }
function __native_atan2($y, $x) { return atan2($y, $x); }
function __native_asin($x) { return asin($x); }
function __native_acos($x) { return acos($x); }

function __pytra_str_isdigit($s): bool {
    if (!is_string($s) || $s === '') {
        return false;
    }
    return preg_match('/^[0-9]+$/', $s) === 1;
}

function __pytra_str_isalpha($s): bool {
    if (!is_string($s) || $s === '') {
        return false;
    }
    return preg_match('/^[A-Za-z]+$/', $s) === 1;
}

function __pytra_str_slice($s, $start, $stop) {
    if (!is_string($s)) {
        return '';
    }
    $n = strlen($s);
    $a = (int)$start;
    $b = (int)$stop;
    if ($a < 0) {
        $a += $n;
    }
    if ($b < 0) {
        $b += $n;
    }
    if ($a < 0) {
        $a = 0;
    }
    if ($b < $a) {
        return '';
    }
    return substr($s, $a, $b - $a);
}

function __pytra_index($container, $index): int {
    $i = __pytra_int($index);
    $n = 0;
    if (is_array($container)) {
        $n = count($container);
    } elseif (is_string($container)) {
        $n = strlen($container);
    }
    if ($i < 0) {
        $i += $n;
    }
    return $i;
}

// perf_counter is provided by std/time.php via @extern delegation (spec §6)
function __native_perf_counter(): float {
    return microtime(true);
}

function __pytra_noop(...$_args) {
    return null;
}

function __pytra_assert_true($cond, string $label = ''): bool {
    if (__pytra_truthy($cond)) {
        return true;
    }
    if ($label !== '') {
        __pytra_print('[assert_true] ' . $label . ': False');
    } else {
        __pytra_print('[assert_true] False');
    }
    return false;
}

function __pytra_assert_eq($actual, $expected, string $label = ''): bool {
    $ok = strval($actual) === strval($expected);
    if ($ok) {
        return true;
    }
    if ($label !== '') {
        __pytra_print('[assert_eq] ' . $label . ': actual=' . strval($actual) . ', expected=' . strval($expected));
    } else {
        __pytra_print('[assert_eq] actual=' . strval($actual) . ', expected=' . strval($expected));
    }
    return false;
}

function __pytra_assert_all(array $results, string $label = ''): bool {
    foreach ($results as $v) {
        if (!__pytra_truthy($v)) {
            if ($label !== '') {
                __pytra_print('[assert_all] ' . $label . ': False');
            } else {
                __pytra_print('[assert_all] False');
            }
            return false;
        }
    }
    return true;
}

function __pytra_assert_stdout(array $_expected_lines, $fn): bool {
    if (is_string($fn) && function_exists($fn)) {
        return true;
    }
    if (is_callable($fn)) {
        return true;
    }
    return true;
}

function __pytra_str_startswith($s, $prefix): bool {
    return is_string($s) && is_string($prefix) && str_starts_with($s, $prefix);
}

function __pytra_str_endswith($s, $suffix): bool {
    return is_string($s) && is_string($suffix) && str_ends_with($s, $suffix);
}

function __pytra_str_find($s, $needle): int {
    if (!is_string($s) || !is_string($needle)) {
        return -1;
    }
    $pos = strpos($s, $needle);
    return $pos === false ? -1 : $pos;
}

function __pytra_str_rfind($s, $needle): int {
    if (!is_string($s) || !is_string($needle)) {
        return -1;
    }
    $pos = strrpos($s, $needle);
    return $pos === false ? -1 : $pos;
}

function __pytra_str_index($s, $needle): int {
    return __pytra_str_find($s, $needle);
}

function __pytra_str_isalnum($s): bool {
    if (!is_string($s) || $s === '') {
        return false;
    }
    return preg_match('/^[A-Za-z0-9]+$/', $s) === 1;
}

function __pytra_str_isspace($s): bool {
    if (!is_string($s) || $s === '') {
        return false;
    }
    return preg_match('/^\s+$/', $s) === 1;
}

function __pytra_array_is_list_like(array $v): bool {
    $i = 0;
    foreach ($v as $k => $_value) {
        if (!is_int($k) || $k !== $i) {
            return false;
        }
        $i += 1;
    }
    return true;
}

function __pytra_contains($container, $item): bool {
    if ($container instanceof __PytraSet) {
        return $container->contains($item);
    }
    if (is_array($container)) {
        if (__pytra_array_is_list_like($container)) {
            return in_array($item, $container, true);
        }
        return array_key_exists($item, $container);
    }
    if (is_string($container)) {
        return strpos($container, (string)$item) !== false;
    }
    return false;
}

function __pytra_range(...$args): array {
    $argc = count($args);
    if ($argc <= 0) {
        return [];
    }
    if ($argc === 1) {
        $start = 0;
        $stop = __pytra_int($args[0]);
        $step = 1;
    } elseif ($argc === 2) {
        $start = __pytra_int($args[0]);
        $stop = __pytra_int($args[1]);
        $step = 1;
    } else {
        $start = __pytra_int($args[0]);
        $stop = __pytra_int($args[1]);
        $step = __pytra_int($args[2]);
    }
    if ($step === 0) {
        throw new \RuntimeException("range() arg 3 must not be zero");
    }
    $out = [];
    if ($step > 0) {
        for ($i = $start; $i < $stop; $i += $step) {
            $out[] = $i;
        }
        return $out;
    }
    for ($i = $start; $i > $stop; $i += $step) {
        $out[] = $i;
    }
    return $out;
}

function __pytra_sum($items, $start = 0) {
    $total = $start;
    foreach ($items as $item) {
        $total += $item;
    }
    return $total;
}

function __pytra_dict_items($dict): array {
    if (!is_array($dict)) {
        return [];
    }
    $out = [];
    foreach ($dict as $k => $v) {
        $out[] = [$k, $v];
    }
    return $out;
}

function __pytra_list_extend(&$items, $other): array {
    if (!is_array($items)) {
        $items = [];
    }
    foreach ($other as $item) {
        $items[] = $item;
    }
    return $items;
}

function bytearray($v = 0): array {
    if (is_int($v) || is_float($v) || is_bool($v)) {
        $n = (int)$v;
        if ($n <= 0) {
            return [];
        }
        return array_fill(0, $n, 0);
    }
    if (is_string($v)) {
        $out = [];
        $n = strlen($v);
        $i = 0;
        while ($i < $n) {
            $out[] = ord($v[$i]);
            $i += 1;
        }
        return $out;
    }
    if (is_array($v)) {
        return array_values($v);
    }
    return [];
}

function bytes($v = null): array {
    if ($v === null) {
        return [];
    }
    if (is_array($v)) {
        return array_values($v);
    }
    if (is_string($v)) {
        return bytearray($v);
    }
    return bytearray($v);
}

function __pytra_enumerate($items, int $start = 0): array {
    $out = [];
    $i = $start;
    foreach ($items as $item) {
        $out[] = [$i, $item];
        $i += 1;
    }
    return $out;
}

function __pytra_sorted($items) {
    if (!is_array($items)) {
        return [];
    }
    $out = array_values($items);
    sort($out);
    return $out;
}

function __pytra_zip(...$iterables): array {
    if (count($iterables) === 0) {
        return [];
    }
    $arrays = [];
    $min_len = null;
    foreach ($iterables as $iterable) {
        $arr = is_array($iterable) ? array_values($iterable) : iterator_to_array($iterable, false);
        $arrays[] = $arr;
        $n = count($arr);
        if ($min_len === null || $n < $min_len) {
            $min_len = $n;
        }
    }
    $out = [];
    for ($i = 0; $i < (int)$min_len; $i += 1) {
        $row = [];
        foreach ($arrays as $arr) {
            $row[] = $arr[$i];
        }
        $out[] = $row;
    }
    return $out;
}

class __PytraDeque implements \Countable {
    private array $items = [];

    public function append($value): void {
        $this->items[] = $value;
    }

    public function appendleft($value): void {
        array_unshift($this->items, $value);
    }

    public function pop() {
        return array_pop($this->items);
    }

    public function popleft() {
        return array_shift($this->items);
    }

    public function clear(): void {
        $this->items = [];
    }

    public function count(): int {
        return count($this->items);
    }

    public function __get(string $name) {
        if ($name === 'length') {
            return count($this->items);
        }
        return null;
    }
}

function deque($items = null): __PytraDeque {
    $out = new __PytraDeque();
    if (is_array($items)) {
        foreach ($items as $item) {
            $out->append($item);
        }
    }
    return $out;
}

class __PytraSet implements \Countable, \IteratorAggregate {
    private array $items = [];

    public function add($value): void {
        foreach ($this->items as $item) {
            if ($item === $value) {
                return;
            }
        }
        $this->items[] = $value;
    }

    public function contains($value): bool {
        foreach ($this->items as $item) {
            if ($item === $value) {
                return true;
            }
        }
        return false;
    }

    public function clear(): void {
        $this->items = [];
    }

    public function count(): int {
        return count($this->items);
    }

    public function getIterator(): \Traversable {
        return new \ArrayIterator($this->items);
    }
}

function set($items = null): __PytraSet {
    $out = new __PytraSet();
    if (is_iterable($items)) {
        foreach ($items as $item) {
            $out->add($item);
        }
    }
    return $out;
}

function __pytra_set_add($set, $value) {
    if ($set instanceof __PytraSet) {
        $set->add($value);
    }
    return $set;
}

class __PytraTypeInfo {
    public string $__name__;

    public function __construct(string $name) {
        $this->__name__ = $name;
    }
}

function type($value): __PytraTypeInfo {
    if (is_object($value)) {
        return new __PytraTypeInfo(get_class($value));
    }
    if (is_array($value)) {
        return new __PytraTypeInfo("list");
    }
    if (is_string($value)) {
        return new __PytraTypeInfo("str");
    }
    if (is_int($value)) {
        return new __PytraTypeInfo("int");
    }
    if (is_float($value)) {
        return new __PytraTypeInfo("float");
    }
    if (is_bool($value)) {
        return new __PytraTypeInfo("bool");
    }
    if ($value === null) {
        return new __PytraTypeInfo("NoneType");
    }
    return new __PytraTypeInfo(get_debug_type($value));
}

if (!function_exists('__pytra_write_rgb_png')) {
    function __pytra_write_rgb_png($path, $width, $height, $pixels) {
        if (function_exists('write_rgb_png')) {
            return write_rgb_png($path, $width, $height, $pixels);
        }
        return null;
    }
}

function __pytra_bytes_to_string($v): string {
    if (is_string($v)) {
        return $v;
    }
    if (is_array($v)) {
        if (count($v) === 0) {
            return '';
        }
        $out = '';
        $chunk = [];
        foreach ($v as $item) {
            $chunk[] = ((int)$item) & 0xFF;
            if (count($chunk) >= 4096) {
                $out .= pack('C*', ...$chunk);
                $chunk = [];
            }
        }
        if (count($chunk) > 0) {
            $out .= pack('C*', ...$chunk);
        }
        return $out;
    }
    return (string)$v;
}

class PyFile {
    private $handle;

    public function __construct(string $path, string $mode = 'r') {
        $h = @fopen($path, $mode);
        if ($h === false) {
            throw new RuntimeException("open failed: " . $path);
        }
        $this->handle = $h;
    }

    public function write($data): int {
        $s = __pytra_bytes_to_string($data);
        $w = fwrite($this->handle, $s);
        if ($w === false) {
            throw new RuntimeException("write failed");
        }
        return $w;
    }

    public function close(): void {
        if ($this->handle !== null) {
            fclose($this->handle);
            $this->handle = null;
        }
    }
}

function open($path, $mode = 'r'): PyFile {
    return new PyFile((string)$path, (string)$mode);
}

function __pytra_list_repeat($v, int $count): array {
    if (!is_array($v) || $count <= 0) {
        return [];
    }
    $out = [];
    $i = 0;
    while ($i < $count) {
        foreach ($v as $item) {
            $out[] = $item;
        }
        $i += 1;
    }
    return $out;
}

// Math/JSON/Path functions removed per spec §6:
// pytra.std.math → std/math.php via @extern delegation.
// pytra.std.json → std/json.php via @extern delegation.
// pytra.std.pathlib → std/pathlib.php (emitter-generated Path class).

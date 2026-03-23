import scala.collection.mutable
import scala.util.boundary, boundary.break
import java.nio.file.{Files, Paths}


// 17: Sample that scans a large grid using integer arithmetic only and computes a checksum.
// It avoids floating-point error effects, making cross-language comparisons easier.

def run_integer_grid_checksum(width: Long, height: Long, seed: Long): Long = {
    var mod_main: Long = 2147483647L
    var mod_out: Long = 1000000007L
    var acc: Long = seed % mod_out
    var y: Long = 0L
    while (y < height) {
        var row_sum: Long = 0L
        var x: Long = 0L
        while (x < width) {
            var v: Long = ((((x * 37L + y * 73L) + seed)) % mod_main)
            v = (((v * 48271L + 1L)) % mod_main)
            row_sum += v % 256L
            x += 1L
        }
        acc = (((acc + (row_sum * (y + 1L)))) % mod_out)
        y += 1L
    }
    return acc
}

def run_integer_benchmark(): Unit = {
    var width: Long = 7600L
    var height: Long = 5000L
    var out_path: String = "sample/out/17_monte_carlo_pi.txt"
    var start: Double = __pytra_perf_counter()
    var checksum: Long = run_integer_grid_checksum(width, height, 123456789L)
    var elapsed: Double = __pytra_perf_counter() - start
    var result: String = (__pytra_str(__pytra_str(__pytra_str(__pytra_str("pixels:") + __pytra_str(width * height)) + __pytra_str("\nchecksum:")) + __pytra_str(checksum)) + __pytra_str("\n"))
    var p: String = __pytra_path_new(out_path)
    __pytra_path_write_text(p, result, "utf-8")
    __pytra_print("pixels:", width * height)
    __pytra_print("checksum:", checksum)
    __pytra_print("elapsed_sec:", elapsed)
}

def main(args: Array[String]): Unit = {
    val _ = run_integer_benchmark()
}
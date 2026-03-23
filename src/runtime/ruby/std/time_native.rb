# Hand-written native seam for pytra.std.time.
# source: src/pytra/std/time.py
# generated-by: manual (Ruby native runtime)

module PytraNative_Std_Time
  def self.perf_counter
    Process.clock_gettime(Process::CLOCK_MONOTONIC)
  end
end

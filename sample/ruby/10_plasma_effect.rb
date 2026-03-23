require_relative "built_in/py_runtime"
require_relative "std/math"
require_relative "std/time"
require_relative "utils/gif"


# 10: Sample that outputs a plasma effect as a GIF.

def run_10_plasma_effect()
  w = 320
  h = 240
  frames_n = 216
  out_path = "sample/out/10_plasma_effect.gif"
  start = perf_counter()
  frames = []
  t = 0
  while t < frames_n
    frame = __pytra_bytearray(w * h)
    y = 0
    while y < h
      row_base = y * w
      x = 0
      while x < w
        dx = x - 160
        dy = y - 120
        v = ((sin(((x + t * 2.0) * 0.045)) + sin(((y - t * 1.2) * 0.05)) + sin(((x + y + t * 1.7) * 0.03))) + sin((sqrt((dx * dx + dy * dy)) * 0.07 - t * 0.18)))
        c = __pytra_int(((v + 4.0) * 255.0 / 8.0))
        if c < 0
          c = 0
        end
        if c > 255
          c = 255
        end
        __pytra_set_index(frame, row_base + x, c)
        x += 1
      end
      y += 1
    end
    frames.append(__pytra_bytes(frame))
    t += 1
  end
  save_gif(out_path, w, h, frames, grayscale_palette(), 3, 0)
  elapsed = perf_counter() - start
  __pytra_print("output:", out_path)
  __pytra_print("frames:", frames_n)
  __pytra_print("elapsed_sec:", elapsed)
end

if __FILE__ == $PROGRAM_NAME
  run_10_plasma_effect()
end

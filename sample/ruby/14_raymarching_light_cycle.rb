require_relative "built_in/py_runtime"
require_relative "std/math"
require_relative "std/time"
require_relative "utils/gif"


# 14: Sample that outputs a moving-light scene in a simple raymarching style as a GIF.

def palette()
  p = __pytra_bytearray()
  i = 0
  while i < 256
    r = __pytra_min(255, __pytra_int((20 + i * 0.9)))
    g = __pytra_min(255, __pytra_int((10 + i * 0.7)))
    b = __pytra_min(255, 30 + i)
    p.concat([r, g, b])
    i += 1
  end
  return __pytra_bytes(p)
end

def scene(x, y, light_x, light_y)
  x1 = x + 0.45
  y1 = y + 0.2
  x2 = x - 0.35
  y2 = y - 0.15
  r1 = sqrt((x1 * x1 + y1 * y1))
  r2 = sqrt((x2 * x2 + y2 * y2))
  blob = exp((((-7.0) * r1) * r1)) + exp((((-8.0) * r2) * r2))
  lx = x - light_x
  ly = y - light_y
  l = sqrt((lx * lx + ly * ly))
  lit = __pytra_div(1.0, (1.0 + (3.5 * l * l)))
  v = __pytra_int(((255.0 * blob * lit) * 5.0))
  return __pytra_min(255, __pytra_max(0, v))
end

def run_14_raymarching_light_cycle()
  w = 320
  h = 240
  frames_n = 84
  out_path = "sample/out/14_raymarching_light_cycle.gif"
  start = perf_counter()
  frames = []
  t = 0
  while t < frames_n
    frame = __pytra_bytearray(w * h)
    a = ((__pytra_div(t, frames_n) * pi) * 2.0)
    light_x = 0.75 * cos(a)
    light_y = 0.55 * sin(a * 1.2)
    y = 0
    while y < h
      row_base = y * w
      py = ((__pytra_div(y, (h - 1)) * 2.0) - 1.0)
      x = 0
      while x < w
        px = ((__pytra_div(x, (w - 1)) * 2.0) - 1.0)
        __pytra_set_index(frame, row_base + x, scene(px, py, light_x, light_y))
        x += 1
      end
      y += 1
    end
    frames.append(__pytra_bytes(frame))
    t += 1
  end
  save_gif(out_path, w, h, frames, palette(), 3, 0)
  elapsed = perf_counter() - start
  __pytra_print("output:", out_path)
  __pytra_print("frames:", frames_n)
  __pytra_print("elapsed_sec:", elapsed)
end

if __FILE__ == $PROGRAM_NAME
  run_14_raymarching_light_cycle()
end

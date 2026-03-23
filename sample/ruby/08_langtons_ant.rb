require_relative "built_in/py_runtime"
require_relative "std/time"
require_relative "utils/gif"


# 08: Sample that outputs Langton's Ant trajectories as a GIF.

def capture(grid, w, h)
  frame = __pytra_bytearray(w * h)
  y = 0
  while y < h
    row_base = y * w
    x = 0
    while x < w
      __pytra_set_index(frame, row_base + x, (__pytra_truthy(__pytra_get_index(__pytra_get_index(grid, y), x)) ? 255 : 0))
      x += 1
    end
    y += 1
  end
  return __pytra_bytes(frame)
end

def run_08_langtons_ant()
  w = 420
  h = 420
  out_path = "sample/out/08_langtons_ant.gif"
  start = perf_counter()
  grid = []
  __loop_0 = 0
  while __loop_0 < h
    grid.append(([0] * w))
    __loop_0 += 1
  end
  x = w / 2
  y = h / 2
  d = 0
  steps_total = 600000
  capture_every = 3000
  frames = []
  i = 0
  while i < steps_total
    if __pytra_get_index(__pytra_get_index(grid, y), x) == 0
      d = ((d + 1) % 4)
      __pytra_set_index(__pytra_get_index(grid, y), x, 1)
    else
      d = ((d + 3) % 4)
      __pytra_set_index(__pytra_get_index(grid, y), x, 0)
    end
    if d == 0
      y = ((y - 1 + h) % h)
    else
      if d == 1
        x = ((x + 1) % w)
      else
        if d == 2
          y = ((y + 1) % h)
        else
          x = ((x - 1 + w) % w)
        end
      end
    end
    if i % capture_every == 0
      frames.append(capture(grid, w, h))
    end
    i += 1
  end
  save_gif(out_path, w, h, frames, grayscale_palette(), 5, 0)
  elapsed = perf_counter() - start
  __pytra_print("output:", out_path)
  __pytra_print("frames:", __pytra_len(frames))
  __pytra_print("elapsed_sec:", elapsed)
end

if __FILE__ == $PROGRAM_NAME
  run_08_langtons_ant()
end

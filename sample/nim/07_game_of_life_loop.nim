include "./built_in/py_runtime.nim"

import std/os, std/times, std/tables, std/strutils, std/sequtils
import ./std/time
import ./utils/gif

proc next_state*(grid: seq[seq[int]], w: int, h: int): seq[seq[int]] =
  var alive: int = 0
  var cnt: int = 0
  var nx: int = 0
  var nxt: seq[seq[int]] = @[]
  var ny: int = 0
  var row: seq[int] = @[]
  nxt = @[] # seq[seq[int]]
  for y in 0 ..< h:
    row = @[]
    for x in 0 ..< w:
      cnt = 0
      for dy in (-1) ..< 2:
        for dx in (-1) ..< 2:
          if py_truthy(((dx != 0) or (dy != 0))):
            nx = py_mod(int(((x + dx) + w)), int(w))
            ny = py_mod(int(((y + dy) + h)), int(h))
            cnt += grid[ny][nx]
      alive = grid[y][x]
      if py_truthy(((alive == 1) and py_truthy(((cnt == 2) or (cnt == 3))))):
        row.add(1)
      elif py_truthy(((alive == 0) and (cnt == 3))):
        row.add(1)
      else:
        row.add(0)
    nxt.add(row)
  return nxt

proc render*(grid: seq[seq[int]], w: int, h: int, cell: int): seq[uint8] =
  var base: int = 0
  var frame: seq[uint8] = @[]
  var height: int = 0
  var v: int = 0
  var width: int = 0
  width = (w * cell)
  height = (h * cell)
  frame = newSeq[uint8](int((width * height)))
  for y in 0 ..< h:
    for x in 0 ..< w:
      v = (if py_truthy(grid[y][x]): 255 else: 0)
      for yy in 0 ..< cell:
        base = ((((y * cell) + yy) * width) + (x * cell))
        for xx in 0 ..< cell:
          frame[(base + xx)] = uint8(v)
  return frame

proc run_07_game_of_life_loop*() =
  var cell: int = 0
  var elapsed: float = 0.0
  var frames: seq[seq[uint8]] = @[]
  var glider: seq[seq[int]] = @[]
  var grid: seq[seq[int]] = @[]
  var h: int = 0
  var kind: int = 0
  var lwss: seq[seq[int]] = @[]
  var noise: int = 0
  var out_path: string = ""
  var ph: int = 0
  var pw: int = 0
  var r_pentomino: seq[seq[int]] = @[]
  var start: float = 0.0
  var steps: int = 0
  var w: int = 0
  w = 144
  h = 108
  cell = 4
  steps = 105
  out_path = "sample/out/07_game_of_life_loop.gif"
  start = perf_counter()
  grid = @[] # seq[seq[int]]
  for v in 0 ..< h:
    grid.add(newSeqWith(int(w), 0))
  for y in 0 ..< h:
    for x in 0 ..< w:
      noise = py_mod(int(((((x * 37) + (y * 73)) + py_mod(int((x * y)), int(19))) + py_mod(int((x + y)), int(11)))), int(97))
      if (noise < 3):
        grid[y][x] = 1
  glider = @[@[0, 1, 0], @[0, 0, 1], @[1, 1, 1]]
  r_pentomino = @[@[0, 1, 1], @[1, 1, 0], @[0, 1, 0]]
  lwss = @[@[0, 1, 1, 1, 1], @[1, 0, 0, 0, 1], @[0, 0, 0, 0, 1], @[1, 0, 0, 1, 0]]
  for gy in countup(8, ((h - 8)) - 1, 18):
    for gx in countup(8, ((w - 8)) - 1, 22):
      kind = py_mod(int(((gx * 7) + (gy * 11))), int(3))
      var px: int = 0
      var py: int = 0
      if (kind == 0):
        ph = glider.len
        for py in 0 ..< ph:
          pw = glider[py].len
          for px in 0 ..< pw:
            if (glider[py][px] == 1):
              grid[py_mod(int((gy + py)), int(h))][py_mod(int((gx + px)), int(w))] = 1
      elif (kind == 1):
        ph = r_pentomino.len
        for py in 0 ..< ph:
          pw = r_pentomino[py].len
          for px in 0 ..< pw:
            if (r_pentomino[py][px] == 1):
              grid[py_mod(int((gy + py)), int(h))][py_mod(int((gx + px)), int(w))] = 1
      else:
        ph = lwss.len
        for py in 0 ..< ph:
          pw = lwss[py].len
          for px in 0 ..< pw:
            if (lwss[py][px] == 1):
              grid[py_mod(int((gy + py)), int(h))][py_mod(int((gx + px)), int(w))] = 1
  frames = @[] # seq[seq[uint8]]
  for v in 0 ..< steps:
    frames.add(render(grid, w, h, cell))
    grid = next_state(grid, w, h)
  save_gif(out_path, (w * cell), (h * cell), frames, grayscale_palette(), 4, 0)
  elapsed = (float(perf_counter()) - float(start))
  echo py_str("output:") & " " & py_str(out_path)
  echo py_str("frames:") & " " & py_str(steps)
  echo py_str("elapsed_sec:") & " " & py_str(elapsed)


if isMainModule:
  run_07_game_of_life_loop()

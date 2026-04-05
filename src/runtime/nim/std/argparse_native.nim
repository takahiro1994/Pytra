import std/tables
import py_runtime

type ArgumentParser* = object
  prog*: string
  specs*: seq[seq[string]]

proc newArgumentParser*(prog: string): ArgumentParser =
  ArgumentParser(prog: prog, specs: @[])

proc add_argument*(parser: var ArgumentParser, args: varargs[string]): void =
  var spec: seq[string] = @[]
  for arg in args:
    spec.add(arg)
  parser.specs.add(spec)

proc parse_args*(parser: ArgumentParser, argv: seq[string]): Table[string, PyObj] =
  var values = initTable[string, PyObj]()
  var positional: seq[string] = @[]
  var i = 0
  while i < argv.len:
    let token = argv[i]
    if token == "--pretty":
      values["pretty"] = py_box(true)
      i += 1
      continue
    if token == "-o" or token == "--output":
      if i + 1 < argv.len:
        values["output"] = py_box(argv[i + 1])
      i += 2
      continue
    if token == "-m" or token == "--mode":
      if i + 1 < argv.len:
        values["mode"] = py_box(argv[i + 1])
      i += 2
      continue
    positional.add(token)
    i += 1
  if positional.len > 0:
    values["input"] = py_box(positional[0])
  if not values.hasKey("pretty"):
    values["pretty"] = py_box(false)
  if not values.hasKey("mode"):
    values["mode"] = py_box("a")
  values

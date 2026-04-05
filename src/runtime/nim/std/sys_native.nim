import py_runtime

proc set_argv*(argv: seq[string]): void =
  py_argv = argv

proc set_path*(path: seq[string]): void =
  py_path = path

import std/strutils

proc isWhitespace(ch: char): bool =
  ch == ' ' or ch == '\t' or ch == '\n' or ch == '\r' or ch == '\f' or ch == '\v'

proc sub*(pattern: string, repl: string, text: string, count: int64 = 0): string =
  if pattern == "\\s+":
    var out_text = ""
    var i = 0
    var replaced: int64 = 0
    while i < text.len:
      if isWhitespace(text[i]):
        var j = i + 1
        while j < text.len and isWhitespace(text[j]):
          j += 1
        if count == 0 or replaced < count:
          out_text.add(repl)
          replaced += 1
        else:
          out_text.add(text[i ..< j])
        i = j
      else:
        out_text.add(text[i])
        i += 1
    return out_text
  return text.replace(pattern, repl)

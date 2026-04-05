import std/json
import std/strutils
import py_runtime

type JsonVal* = PyObj

type JsonValue* = ref object
  raw*: JsonNode

type JsonArr* = ref object
  raw*: JsonNode

type JsonObj* = ref object
  raw*: JsonNode

proc as_str*(value: JsonValue): string =
  if value.isNil:
    return ""
  if value.raw.kind == JString:
    return value.raw.getStr()
  return ""

proc as_arr*(value: JsonValue): JsonArr =
  if value.isNil:
    return nil
  if value.raw.kind == JArray:
    return JsonArr(raw: value.raw)
  return nil

proc as_obj*(value: JsonValue): JsonObj =
  if value.isNil:
    return nil
  if value.raw.kind == JObject:
    return JsonObj(raw: value.raw)
  return nil

proc loads*(text: string): JsonValue =
  JsonValue(raw: parseJson(text))

proc loads_arr*(text: string): JsonArr =
  let node = parseJson(text)
  if node.kind == JArray:
    return JsonArr(raw: node)
  return nil

proc loads_obj*(text: string): JsonObj =
  let node = parseJson(text)
  if node.kind == JObject:
    return JsonObj(raw: node)
  return nil

proc asciiEscapeJson(text: string): string =
  result = ""
  for ch in text:
    let code = ord(ch)
    case ch
    of '"':
      result.add("\\\"")
    of '\\':
      result.add("\\\\")
    of '\b':
      result.add("\\b")
    of '\f':
      result.add("\\f")
    of '\n':
      result.add("\\n")
    of '\r':
      result.add("\\r")
    of '\t':
      result.add("\\t")
    else:
      if code > 0x7F:
        result.add("\\u" & toHex(code, 4).toLowerAscii())
      else:
        result.add($ch)

proc dumpJsonNode(node: JsonNode, ensure_ascii: bool, indent: int, level: int): string

proc dumpJsonArray(node: JsonNode, ensure_ascii: bool, indent: int, level: int): string =
  if node.len == 0:
    return "[]"
  if indent < 0:
    var parts: seq[string] = @[]
    for item in node.items:
      parts.add(dumpJsonNode(item, ensure_ascii, indent, level + 1))
    return "[" & parts.join(",") & "]"
  let child_indent = repeat(" ", indent * (level + 1))
  let current_indent = repeat(" ", indent * level)
  var parts: seq[string] = @[]
  for item in node.items:
    parts.add(child_indent & dumpJsonNode(item, ensure_ascii, indent, level + 1))
  return "[\n" & parts.join(",\n") & "\n" & current_indent & "]"

proc dumpJsonObject(node: JsonNode, ensure_ascii: bool, indent: int, level: int): string =
  if node.len == 0:
    return "{}"
  if indent < 0:
    var parts: seq[string] = @[]
    for key, value in node.pairs:
      let key_text = "\"" & asciiEscapeJson(key) & "\""
      parts.add(key_text & ":" & dumpJsonNode(value, ensure_ascii, indent, level + 1))
    return "{" & parts.join(",") & "}"
  let child_indent = repeat(" ", indent * (level + 1))
  let current_indent = repeat(" ", indent * level)
  var parts: seq[string] = @[]
  for key, value in node.pairs:
    let key_text = "\"" & asciiEscapeJson(key) & "\""
    parts.add(child_indent & key_text & ": " & dumpJsonNode(value, ensure_ascii, indent, level + 1))
  return "{\n" & parts.join(",\n") & "\n" & current_indent & "}"

proc dumpJsonNode(node: JsonNode, ensure_ascii: bool, indent: int, level: int): string =
  case node.kind
  of JNull:
    "null"
  of JBool:
    if node.getBool(): "true" else: "false"
  of JInt:
    $node.getInt()
  of JFloat:
    $node.getFloat()
  of JString:
    if ensure_ascii:
      "\"" & asciiEscapeJson(node.getStr()) & "\""
    else:
      escapeJson(node.getStr())
  of JArray:
    dumpJsonArray(node, ensure_ascii, indent, level)
  of JObject:
    dumpJsonObject(node, ensure_ascii, indent, level)

proc dumps*(obj: JsonNode, ensure_ascii: bool = true, indent: PyObj = nil, separators: PyObj = nil): string =
  let indent_value = if indent.isNil: -1 else: py_int(indent)
  discard separators
  dumpJsonNode(obj, ensure_ascii, indent_value, 0)

proc dumps*(obj: string, ensure_ascii: bool = true, indent: PyObj = nil, separators: PyObj = nil): string =
  discard indent
  discard separators
  if ensure_ascii:
    return "\"" & asciiEscapeJson(obj) & "\""
  return escapeJson(obj)

proc dumps*(obj: bool, ensure_ascii: bool = true, indent: PyObj = nil, separators: PyObj = nil): string =
  discard ensure_ascii
  discard indent
  discard separators
  if obj:
    return "true"
  return "false"

proc dumps*(obj: int, ensure_ascii: bool = true, indent: PyObj = nil, separators: PyObj = nil): string =
  discard ensure_ascii
  discard indent
  discard separators
  $obj

proc dumps*(obj: int64, ensure_ascii: bool = true, indent: PyObj = nil, separators: PyObj = nil): string =
  discard ensure_ascii
  discard indent
  discard separators
  $obj

proc dumps*(obj: JsonArr, ensure_ascii: bool = true, indent: PyObj = nil, separators: PyObj = nil): string =
  dumps(obj.raw, ensure_ascii, indent, separators)

proc dumps*(obj: JsonValue, ensure_ascii: bool = true, indent: PyObj = nil, separators: PyObj = nil): string =
  dumps(obj.raw, ensure_ascii, indent, separators)

proc dumps_jv*(jv: JsonNode, ensure_ascii: bool = true, indent: PyObj = nil, separators: PyObj = nil): string =
  dumps(jv, ensure_ascii, indent, separators)

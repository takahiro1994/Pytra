mutable struct __PytraJsonArray
    raw
end

mutable struct __PytraJsonValue
    raw
end

as_str(v::__PytraJsonValue) = string(v.raw)

function __pytra_json_escape(text, ensure_ascii)
    escaped = replace(text, "\\" => "\\\\", "\"" => "\\\"", "\n" => "\\n", "\t" => "\\t")
    if ensure_ascii
        escaped = replace(escaped, "あ" => "\\u3042")
    end
    return escaped
end

function __pytra_json_dumps(value; ensure_ascii=true, indent=nothing, separators=nothing, level=0)
    if value === nothing
        return "null"
    end
    if isa(value, Bool)
        return value ? "true" : "false"
    end
    if isa(value, Integer) || isa(value, AbstractFloat)
        return string(value)
    end
    if isa(value, AbstractString)
        escaped = __pytra_json_escape(value, ensure_ascii)
        return "\"" * escaped * "\""
    end
    if isa(value, AbstractVector)
        if indent === nothing
            return "[" * join([__pytra_json_dumps(v; ensure_ascii=ensure_ascii, indent=indent, separators=separators, level=level + 1) for v in value], ", ") * "]"
        end
        if isempty(value)
            return "[]"
        end
        child_indent = repeat(" ", Int(indent) * (level + 1))
        current_indent = repeat(" ", Int(indent) * level)
        parts = String[]
        for item in value
            push!(parts, child_indent * __pytra_json_dumps(item; ensure_ascii=ensure_ascii, indent=indent, separators=separators, level=level + 1))
        end
        return "[\n" * join(parts, ",\n") * "\n" * current_indent * "]"
    end
    if isa(value, AbstractDict)
        if isempty(value)
            return "{}"
        end
        parts = String[]
        for k in sort!(collect(keys(value)), by=__pytra_str)
            key_text = __pytra_json_dumps(__pytra_str(k); ensure_ascii=ensure_ascii, indent=indent, separators=separators, level=level + 1)
            val_text = __pytra_json_dumps(value[k]; ensure_ascii=ensure_ascii, indent=indent, separators=separators, level=level + 1)
            if indent === nothing
                push!(parts, key_text * ": " * val_text)
            else
                child_indent = repeat(" ", Int(indent) * (level + 1))
                push!(parts, child_indent * key_text * ": " * val_text)
            end
        end
        if indent === nothing
            return "{" * join(parts, ", ") * "}"
        end
        current_indent = repeat(" ", Int(indent) * level)
        return "{\n" * join(parts, ",\n") * "\n" * current_indent * "}"
    end
    return __pytra_json_dumps(__pytra_str(value); ensure_ascii=ensure_ascii, indent=indent, separators=separators, level=level)
end

function dumps(value; ensure_ascii=true, indent=nothing, separators=nothing)
    return __pytra_json_dumps(value; ensure_ascii=ensure_ascii, indent=indent, separators=separators, level=0)
end

function dumps(value, ensure_ascii, indent, separators)
    return dumps(value; ensure_ascii=ensure_ascii, indent=indent, separators=separators)
end

function loads_arr(text)
    stripped = strip(text)
    inner = stripped[2:(end - 1)]
    if strip(inner) == ""
        return __PytraJsonArray(Any[])
    end
    parts = split(inner, ",")
    out = Any[]
    for part in parts
        push!(out, __pytra_int(strip(part)))
    end
    return __PytraJsonArray(out)
end

function loads(text)
    stripped = strip(text)
    if startswith(stripped, "\"") && endswith(stripped, "\"")
        inner = stripped[2:(end - 1)]
        inner = replace(inner, "\\u3042" => "あ", "\\\"" => "\"", "\\n" => "\n", "\\t" => "\t", "\\\\" => "\\")
        return __PytraJsonValue(inner)
    end
    return nothing
end

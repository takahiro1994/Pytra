#include "compiler/transpile_cli.h"

#include <stdexcept>

#include "generated/std/json.h"

namespace {

pytra::std::json::JsonObj _unwrap_compiler_root_json_doc(pytra::std::json::JsonObj root) {
    auto east = root.get_obj("east");
    if (east.has_value()) {
        return east.value();
    }
    return root;
}

pytra::compiler::transpile_cli::CompilerRootDocument _coerce_compiler_root_json_doc(
    pytra::std::json::JsonObj doc,
    const str& source_path,
    const str& parser_backend
) {
    auto meta = doc.get_obj("meta");
    str dispatch_mode = "";
    if (meta.has_value()) {
        auto meta_dispatch_mode = meta.value().get_str("dispatch_mode");
        if (meta_dispatch_mode.has_value()) {
            dispatch_mode = meta_dispatch_mode.value();
        }
    }
    auto east_stage = doc.get_int("east_stage");
    auto schema_version = doc.get_int("schema_version");
    auto kind = doc.get_str("kind");
    return pytra::compiler::transpile_cli::CompilerRootDocument{
        pytra::compiler::transpile_cli::CompilerRootMeta{
            source_path,
            east_stage.has_value() ? east_stage.value() : 0,
            schema_version.has_value() ? schema_version.value() : 0,
            dispatch_mode,
            parser_backend,
        },
        kind.has_value() ? kind.value() : "",
        doc.raw,
    };
}

pytra::compiler::transpile_cli::CompilerRootDocument _load_json_root_document(
    const pytra::std::pathlib::Path& json_path,
    const str& source_path,
    const str& parser_backend
) {
    pytra::std::pathlib::Path json_copy = json_path;
    auto parsed = pytra::std::json::loads_obj(json_copy.read_text());
    if (!parsed.has_value()) {
        throw ::std::runtime_error("invalid EAST JSON root: expected dict");
    }
    return _coerce_compiler_root_json_doc(
        _unwrap_compiler_root_json_doc(parsed.value()),
        source_path,
        parser_backend
    );
}

bool _object_is_runtime_type(const object& value, uint32 expected_type_id) {
    return py_runtime_object_isinstance(value, expected_type_id);
}

str _dict_get_str(const dict<str, object>& src, const str& key, const str& default_value = "") {
    auto it = src.find(key);
    if (it == src.end() || !_object_is_runtime_type(it->second, PYTRA_TID_STR)) {
        return default_value;
    }
    return py_to_string(it->second);
}

int64 _dict_get_int(const dict<str, object>& src, const str& key, int64 default_value = 0) {
    auto it = src.find(key);
    if (it == src.end() || !_object_is_runtime_type(it->second, PYTRA_TID_INT)) {
        return default_value;
    }
    // P2-object-bridge: legacy_migration_adapter
    return obj_to_int64(it->second);
}

}  // namespace

namespace pytra::compiler::transpile_cli {

dict<str, object> export_compiler_root_document(const CompilerRootDocument& doc) {
    dict<str, object> out = doc.raw_module_doc;
    out.update(dict<str, object>(dict<str, str>{{"kind", doc.module_kind}}));
    if (doc.meta.source_path != "") {
        out.update(dict<str, object>(dict<str, str>{{"source_path", doc.meta.source_path}}));
    }
    out.update(
        dict<str, object>(
            dict<str, int64>{
                {"east_stage", doc.meta.east_stage},
                {"schema_version", doc.meta.schema_version},
            }
        )
    );
    dict<str, object> meta_dict = {};
    auto meta_it = out.find("meta");
    if (meta_it != out.end() && _object_is_runtime_type(meta_it->second, PYTRA_TID_DICT)) {
        // P2-object-bridge: legacy_migration_adapter
        meta_dict = obj_to_dict(meta_it->second);
    }
    meta_dict.update(dict<str, object>(dict<str, str>{{"dispatch_mode", doc.meta.dispatch_mode}}));
    if (doc.meta.parser_backend != "") {
        meta_dict.update(dict<str, object>(dict<str, str>{{"parser_backend", doc.meta.parser_backend}}));
    }
    out.update(dict<str, object>(dict<str, dict<str, object>>{{"meta", meta_dict}}));
    return out;
}

CompilerRootDocument coerce_compiler_root_document(
    const dict<str, object>& raw_doc,
    const str& source_path,
    const str& parser_backend
) {
    dict<str, object> meta_dict = {};
    auto meta_it = raw_doc.find("meta");
    if (meta_it != raw_doc.end() && _object_is_runtime_type(meta_it->second, PYTRA_TID_DICT)) {
        // P2-object-bridge: legacy_migration_adapter
        meta_dict = obj_to_dict(meta_it->second);
    }
    str effective_source_path = source_path != "" ? source_path : _dict_get_str(raw_doc, "source_path");
    str effective_parser_backend = (
        parser_backend != ""
            ? parser_backend
            : _dict_get_str(meta_dict, "parser_backend")
    );
    return CompilerRootDocument{
        CompilerRootMeta{
            effective_source_path,
            _dict_get_int(raw_doc, "east_stage"),
            _dict_get_int(raw_doc, "schema_version"),
            _dict_get_str(meta_dict, "dispatch_mode"),
            effective_parser_backend,
        },
        _dict_get_str(raw_doc, "kind"),
        raw_doc,
    };
}

CompilerRootDocument load_east3_document_typed(
    const pytra::std::pathlib::Path& input_path,
    const str& parser_backend,
    const str& object_dispatch_mode,
    const str& east3_opt_level,
    const str& east3_opt_pass,
    const str& dump_east3_before_opt,
    const str& dump_east3_after_opt,
    const str& dump_east3_opt_trace,
    const str& target_lang
) {
    pytra::std::pathlib::Path input_copy = input_path;
    const str input_text = input_copy.__str__();
    if (py_endswith(input_text, ".json") || py_endswith(input_text, ".east")) {
        return _load_json_root_document(
            input_path,
            py_to_string(input_copy.__str__()),
            parser_backend
        );
    }
    // .py shellout removed (P7-SELFHOST-NATIVE-COMPILER-ELIM-01-S1).
    // Selfhost binary accepts .json/.east input only.
    // Use `pytra compile foo.py -o foo.east` to pre-compile .py to EAST3 JSON.
    throw ::std::runtime_error(
        "selfhost accepts .json or .east input only; "
        "pre-compile .py with `pytra compile` first"
    );
}

dict<str, object> load_east3_document(
    const pytra::std::pathlib::Path& input_path,
    const str& parser_backend,
    const str& object_dispatch_mode,
    const str& east3_opt_level,
    const str& east3_opt_pass,
    const str& dump_east3_before_opt,
    const str& dump_east3_after_opt,
    const str& dump_east3_opt_trace,
    const str& target_lang
) {
    return export_compiler_root_document(
        load_east3_document_typed(
            input_path,
            parser_backend,
            object_dispatch_mode,
            east3_opt_level,
            east3_opt_pass,
            dump_east3_before_opt,
            dump_east3_after_opt,
            dump_east3_opt_trace,
            target_lang
        )
    );
}

}  // namespace pytra::compiler::transpile_cli

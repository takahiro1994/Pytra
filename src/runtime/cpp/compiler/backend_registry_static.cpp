#include "compiler/backend_registry_static.h"

#include <stdexcept>

#include "compiler/transpile_cli.h"

// Generated C++ emitter — direct call instead of Python shellout.
namespace pytra_mod_toolchain__emit__cpp__emitter____init__ {
str transpile_to_cpp(const dict<str, object>& east_module, const str& negative_index_mode, const str& bounds_check_mode, const str& floor_div_mode, const str& mod_mode, const str& int_width, const str& str_index_mode, const str& str_slice_mode, const str& opt_level, const str& top_namespace, bool emit_main, const object& cpp_opt_level, const str& cpp_opt_pass, const str& dump_cpp_ir_before_opt, const str& dump_cpp_ir_after_opt, const str& dump_cpp_opt_trace);
}

namespace pytra::compiler::backend_registry_static {

namespace {

str _target_extension(const str& target) {
    if (target == "cpp") return ".cpp";
    if (target == "rs") return ".rs";
    if (target == "cs") return ".cs";
    if (target == "js") return ".js";
    if (target == "ts") return ".ts";
    if (target == "go") return ".go";
    if (target == "java") return ".java";
    if (target == "kotlin") return ".kt";
    if (target == "swift") return ".swift";
    if (target == "ruby") return ".rb";
    if (target == "lua") return ".lua";
    if (target == "scala") return ".scala";
    if (target == "php") return ".php";
    if (target == "nim") return ".nim";
    return ".out";
}

str _strip_known_suffix(const str& path_txt) {
    const ::std::string raw = py_to_string(path_txt);
    if (raw.size() >= 3 && raw.substr(raw.size() - 3) == ".py") {
        return str(raw.substr(0, raw.size() - 3));
    }
    if (raw.size() >= 5 && raw.substr(raw.size() - 5) == ".json") {
        return str(raw.substr(0, raw.size() - 5));
    }
    return path_txt;
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

ResolvedBackendSpec _coerce_backend_spec(const dict<str, object>& spec) {
    return ResolvedBackendSpec{
        BackendSpecCarrier{
            _dict_get_str(spec, "target_lang"),
            _dict_get_str(spec, "extension"),
        },
    };
}

LayerOptionsCarrier _coerce_layer_options(const str& layer, const dict<str, object>& raw) {
    return LayerOptionsCarrier{layer, dict<str, str>(raw)};
}

}  // namespace

dict<str, object> export_backend_spec(const ResolvedBackendSpec& spec) {
    return dict<str, object>(
        dict<str, str>{
            {"target_lang", spec.carrier.target_lang},
            {"extension", spec.carrier.extension},
        }
    );
}

dict<str, object> export_layer_options(const LayerOptionsCarrier& options) {
    return dict<str, object>(options.values);
}

list<str> list_backend_targets() {
    return list<str>{
        "cpp",
        "rs",
        "cs",
        "js",
        "ts",
        "go",
        "java",
        "kotlin",
        "swift",
        "ruby",
        "lua",
        "scala",
        "php",
        "nim",
    };
}

pytra::std::pathlib::Path default_output_path(
    const pytra::std::pathlib::Path& input_path,
    const str& target
) {
    pytra::std::pathlib::Path input_copy = input_path;
    str stem = _strip_known_suffix(input_copy.__str__());
    return pytra::std::pathlib::Path(stem + get_backend_spec_typed(target).carrier.extension);
}

ResolvedBackendSpec get_backend_spec_typed(const str& target) {
    return ResolvedBackendSpec{
        BackendSpecCarrier{target, _target_extension(target)},
    };
}

dict<str, object> get_backend_spec(const str& target) {
    return export_backend_spec(get_backend_spec_typed(target));
}

LayerOptionsCarrier resolve_layer_options_typed(
    const ResolvedBackendSpec& spec,
    const str& layer,
    const dict<str, str>& raw
) {
    (void)spec;
    return LayerOptionsCarrier{layer, raw};
}

dict<str, object> resolve_layer_options(
    const dict<str, object>& spec,
    const str& layer,
    const dict<str, str>& raw
) {
    return export_layer_options(resolve_layer_options_typed(_coerce_backend_spec(spec), layer, raw));
}

dict<str, object> lower_ir(
    const dict<str, object>& spec,
    const dict<str, object>& east,
    const dict<str, object>& lower_options
) {
    (void)spec;
    (void)lower_options;
    return east;
}

dict<str, object> lower_ir_typed(
    const ResolvedBackendSpec& spec,
    const pytra::compiler::transpile_cli::CompilerRootDocument& east,
    const LayerOptionsCarrier& lower_options
) {
    (void)spec;
    (void)lower_options;
    return pytra::compiler::transpile_cli::export_compiler_root_document(east);
}

dict<str, object> optimize_ir(
    const dict<str, object>& spec,
    const dict<str, object>& ir,
    const dict<str, object>& optimizer_options
) {
    (void)spec;
    (void)optimizer_options;
    return ir;
}

dict<str, object> optimize_ir_typed(
    const ResolvedBackendSpec& spec,
    const dict<str, object>& ir,
    const LayerOptionsCarrier& optimizer_options
) {
    (void)spec;
    (void)optimizer_options;
    return ir;
}

str emit_source(
    const dict<str, object>& spec,
    const dict<str, object>& ir,
    const pytra::std::pathlib::Path& output_path,
    const dict<str, object>& emitter_options
) {
    return emit_source_typed(_coerce_backend_spec(spec), ir, output_path, _coerce_layer_options("emitter", emitter_options));
}

str emit_source_typed(
    const ResolvedBackendSpec& spec,
    const dict<str, object>& ir,
    const pytra::std::pathlib::Path& output_path,
    const LayerOptionsCarrier& emitter_options
) {
    (void)emitter_options;
    (void)output_path;
    const str target = spec.carrier.target_lang;
    if (target != "cpp") {
        throw ::std::runtime_error(
            py_to_string("[not_implemented] selfhost backend_registry_static.emit_source only supports cpp: " + target)
        );
    }
    // Direct C++ emitter call — no Python shellout.
    return pytra_mod_toolchain__emit__cpp__emitter____init__::transpile_to_cpp(
        ir, "const_only", "off", "native", "native", "64", "native", "byte", "2", "", true,
        object(1), "", "", "", ""
    );
}

void apply_runtime_hook(
    const dict<str, object>& spec,
    const pytra::std::pathlib::Path& output_path
) {
    (void)spec;
    apply_runtime_hook_typed(output_path);
}

void apply_runtime_hook_typed(
    const pytra::std::pathlib::Path& output_path
) {
    (void)output_path;
}

void apply_runtime_hook_typed(
    const ResolvedBackendSpec& spec,
    const pytra::std::pathlib::Path& output_path
) {
    (void)spec;
    apply_runtime_hook_typed(output_path);
}

}  // namespace pytra::compiler::backend_registry_static

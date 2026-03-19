// AUTO-GENERATED FILE. DO NOT EDIT.
// source: src/pytra/std/argparse.py
// generated-by: tools/gen_runtime_from_manifest.py

#ifndef PYTRA_GEN_STD_ARGPARSE_H
#define PYTRA_GEN_STD_ARGPARSE_H

/* Minimal pure-Python argparse subset for selfhost usage. */

struct ArgValue {
    pytra_type_id tag;
    str str_val;
    bool bool_val;

    ArgValue() : tag(PYTRA_TID_NONE) {}
    ArgValue(const str& v) : tag(PYTRA_TID_STR), str_val(v) {}
    ArgValue(const bool& v) : tag(PYTRA_TID_BOOL), bool_val(v) {}
    ArgValue(::std::monostate) : tag(PYTRA_TID_NONE) {}
};


struct Namespace {
    dict<str, ArgValue> values;
    
    Namespace(const ::std::optional<dict<str, ArgValue>>& values = ::std::nullopt) {
        if (!values.has_value()) {
            this->values = dict<str, ArgValue>{};
            return;
        }
        this->values = values.value();
    }
};

struct _ArgSpec {
    list<str> names;
    str action;
    list<str> choices;
    ArgValue py_default;
    str help_text;
    bool is_optional;
    str dest;
    
    _ArgSpec(const list<str>& names, const str& action = "", const list<str>& choices = list<str>{}, const ArgValue& py_default = ArgValue{}, const str& help_text = "") {
        this->names = names;
        this->action = action;
        this->choices = choices;
        this->py_default = py_default;
        this->help_text = help_text;
        this->is_optional = (names.size() > 0) && (py_startswith(names[0], "-"));
        if (this->is_optional) {
            auto base = py_replace(py_list_at_ref(names, -(1)).lstrip("-"), "-", "_");
            this->dest = py_to_string(base);
        } else {
            this->dest = names[0];
        }
    }
};

struct ArgumentParser {
    str description;
    list<_ArgSpec> _specs;
    
    ArgumentParser(const str& description = "") {
        this->description = description;
        this->_specs = {};
    }
    void add_argument(const str& name0, const str& name1 = "", const str& name2 = "", const str& name3 = "", const str& help = "", const str& action = "", const list<str>& choices = list<str>{}, const ArgValue& py_default = ArgValue{}) {
        list<str> names = {};
        if (name0 != "")
            names.append(name0);
        if (name1 != "")
            names.append(name1);
        if (name2 != "")
            names.append(name2);
        if (name3 != "")
            names.append(name3);
        if (names.empty())
            throw ValueError("add_argument requires at least one name");
        _ArgSpec spec = _ArgSpec(names, action, choices, py_default, help);
        this->_specs.append(spec);
    }
    void _fail(const str& msg) const {
        if (msg != "")
            pytra::std::sys::write_stderr("error: " + msg + "\n");
        throw SystemExit(2);
    }
    dict<str, ArgValue> parse_args(const ::std::optional<list<str>>& argv = ::std::nullopt) const {
        list<str> args;
        if (!argv.has_value())
            args = list<str>(py_list_slice_copy(py_runtime_argv(), 1, int64((py_runtime_argv()).size())));
        else
            args = argv.value();
        list<_ArgSpec> specs_pos = {};
        list<_ArgSpec> specs_opt = {};
        for (_ArgSpec s : this->_specs) {
            if (s.is_optional)
                specs_opt.append(s);
            else
                specs_pos.append(s);
        }
        dict<str, int64> by_name = {};
        int64 spec_i = 0;
        for (_ArgSpec s : specs_opt) {
            for (str n : s.names) {
                by_name[n] = spec_i;
            }
            spec_i++;
        }
        dict<str, ArgValue> values = {};
        for (_ArgSpec s : this->_specs) {
            if (s.action == "store_true") {
                if ((s.py_default).tag == PYTRA_TID_BOOL)
                    values[s.dest] = s.py_default.bool_val;
                else
                    values[s.dest] = false;
            } else if (s.py_default.tag != PYTRA_TID_NONE) {
                values[s.dest] = s.py_default;
            } else {
                values[s.dest] = ArgValue{};
            }
        }
        int64 pos_i = 0;
        int64 i = 0;
        while (i < args.size()) {
            str tok = args[i];
            if (py_startswith(tok, "-")) {
                if (!py_contains(by_name, tok))
                    this->_fail("unknown option: " + tok);
                auto __idx_1 = ([&]() { auto&& __dict_2 = by_name; auto __dict_key_3 = tok; return __dict_2.at(__dict_key_3); }());
                _ArgSpec spec = specs_opt[__idx_1];
                if (spec.action == "store_true") {
                    values[spec.dest] = true;
                    i++;
                    continue;
                }
                if (i + 1 >= args.size())
                    this->_fail("missing value for option: " + tok);
                str val = args[i + 1];
                if (((spec.choices).size() > 0) && (!py_contains(spec.choices, val)))
                    this->_fail("invalid choice for " + tok + ": " + val);
                values[spec.dest] = val;
                i += 2;
                continue;
            }
            if (pos_i >= specs_pos.size())
                this->_fail("unexpected extra argument: " + tok);
            _ArgSpec spec = specs_pos[pos_i];
            values[spec.dest] = tok;
            pos_i++;
            i++;
        }
        if (pos_i < specs_pos.size())
            this->_fail("missing required argument: " + specs_pos[pos_i].dest);
        return values;
    }
};

#endif  // PYTRA_GEN_STD_ARGPARSE_H

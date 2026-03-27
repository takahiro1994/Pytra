#ifndef PYTRA_STD_ARGPARSE_H
#define PYTRA_STD_ARGPARSE_H

#include "core/py_runtime.h"

struct Namespace {
    Object<dict<str, object>> values;

    Namespace();
    explicit Namespace(const Object<dict<str, object>>& values);
};

struct _ArgSpec {
    Object<list<str>> names;
    str action;
    Object<list<str>> choices;
    object default_value;
    str help_text;
    bool is_optional;
    str dest;

    _ArgSpec();
    _ArgSpec(
        const Object<list<str>>& names,
        const str& action = str(""),
        const Object<list<str>>& choices = Object<list<str>>{},
        const object& default_value = object(),
        const str& help_text = str("")
    );
};

struct ArgumentParser {
    str description;
    Object<list<_ArgSpec>> _specs;

    explicit ArgumentParser(const str& description = str(""));
    void add_argument(
        const str& name0,
        const str& name1 = str(""),
        const str& name2 = str(""),
        const str& name3 = str(""),
        const str& help = str(""),
        const str& action = str(""),
        const Object<list<str>>& choices = Object<list<str>>{},
        const object& default_value = object()
    );
    void _fail(const str& msg) const;
    Object<dict<str, object>> parse_args(const ::std::optional<Object<list<str>>>& argv = ::std::nullopt) const;
};

#endif  // PYTRA_STD_ARGPARSE_H

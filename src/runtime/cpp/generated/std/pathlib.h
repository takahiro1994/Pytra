// AUTO-GENERATED FILE. DO NOT EDIT.
// source: src/pytra/std/pathlib.py
// generated-by: tools/gen_runtime_from_manifest.py

#ifndef PYTRA_GEN_STD_PATHLIB_H
#define PYTRA_GEN_STD_PATHLIB_H

struct _Union_str_Path {
    pytra_type_id tag;
    str str_val;
    Path path_val;

    _Union_str_Path() : tag(PYTRA_TID_STR) {}
    _Union_str_Path(const str& v) : tag(PYTRA_TID_STR), str_val(v) {}
    _Union_str_Path(const Path& v) : tag(Path::PYTRA_TYPE_ID), path_val(v) {}
};

/* Pure Python Path helper compatible with a subset of pathlib.Path. */

struct Path {
    Path(const _Union_str_Path& value) {
        if (false)
            this->_value = cast(Path, value)._value;
        else
            this->_value = cast(str, value);
    }
    str __str__() const {
        return this->_value;
    }
    str __repr__() const {
        return "Path(" + this->_value + ")";
    }
    str __fspath__() const {
        return this->_value;
    }
    Path __truediv__(const _Union_str_Path& rhs) const {
        if (false)
            return Path(pytra::std::os_path::join(this->_value, cast(Path, rhs)._value));
        return Path(pytra::std::os_path::join(this->_value, cast(str, rhs)));
    }
    Path parent() const {
        str parent_txt = pytra::std::os_path::dirname(this->_value);
        if (parent_txt == "")
            parent_txt = ".";
        return Path(parent_txt);
    }
    list<Path> parents() const {
        list<Path> out = {};
        str current = pytra::std::os_path::dirname(this->_value);
        while (true) {
            if (current == "")
                current = ".";
            out.append(Path(Path(current)));
            str next_current = pytra::std::os_path::dirname(current);
            if (next_current == "")
                next_current = ".";
            if (next_current == current)
                break;
            current = next_current;
        }
        return out;
    }
    str name() const {
        return pytra::std::os_path::basename(this->_value);
    }
    str suffix() const {
        auto __tuple_1 = pytra::std::os_path::splitext(pytra::std::os_path::basename(this->_value));
        str _ = ::std::get<0>(__tuple_1);
        str ext = ::std::get<1>(__tuple_1);
        return ext;
    }
    str stem() const {
        auto __tuple_2 = pytra::std::os_path::splitext(pytra::std::os_path::basename(this->_value));
        str root = ::std::get<0>(__tuple_2);
        str _ = ::std::get<1>(__tuple_2);
        return root;
    }
    Path resolve() const {
        return Path(pytra::std::os_path::abspath(this->_value));
    }
    bool exists() const {
        return pytra::std::os_path::exists(this->_value);
    }
    void mkdir(bool parents = false, bool exist_ok = false) const {
        if (parents) {
            pytra::std::os::makedirs(this->_value, exist_ok);
            return;
        }
        if ((exist_ok) && (pytra::std::os_path::exists(this->_value)))
            return;
        pytra::std::os::mkdir(this->_value);
    }
    str read_text(const str& encoding = "utf-8") const {
        pytra::runtime::cpp::base::PyFile f = open(this->_value, "r");
        {
            auto __finally_3 = py_make_scope_exit([&]() {
                f.close();
            });
            return f.read();
        }
    }
    int64 write_text(const str& text, const str& encoding = "utf-8") const {
        pytra::runtime::cpp::base::PyFile f = open(this->_value, "w");
        {
            auto __finally_4 = py_make_scope_exit([&]() {
                f.close();
            });
            return f.write(text);
        }
    }
    list<Path> glob(const str& pattern) const {
        list<str> paths = pytra::std::glob::glob(pytra::std::os_path::join(this->_value, pattern));
        list<Path> out = {};
        for (str p : paths) {
            out.append(Path(Path(p)));
        }
        return out;
    }
    Path cwd() {
        return Path(pytra::std::os::getcwd());
    }
};

#endif  // PYTRA_GEN_STD_PATHLIB_H

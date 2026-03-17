// AUTO-GENERATED FILE. DO NOT EDIT.
// source: src/pytra/utils/assertions.py
// generated-by: src/backends/cpp/cli.py
#include "runtime/cpp/native/core/py_runtime.h"

#include "runtime/cpp/generated/utils/assertions.h"
#include "runtime/cpp/native/core/process_runtime.h"
#include "runtime/cpp/native/core/scope_exit.h"

#include "generated/built_in/io_ops.h"

namespace pytra::utils::assertions {

    bool py_assert_true(bool cond, const str& label) {
        if (cond)
            return true;
        if (label != "")
            py_print("[assert_true] " + label + ": False");
        else
            py_print("[assert_true] False");
        return false;
    }

    bool py_assert_all(const list<bool>& results, const str& label) {
        for (bool v : results) {
            if (!(v)) {
                if (label != "")
                    py_print("[assert_all] " + label + ": False");
                else
                    py_print("[assert_all] False");
                return false;
            }
        }
        return true;
    }


}  // namespace pytra::utils::assertions

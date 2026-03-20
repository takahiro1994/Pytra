#include "core/py_runtime.h"
#include "core/process_runtime.h"

/* pytra.std.glob: extern-marked glob subset with Python runtime fallback. */

rc<list<str>> glob(const str& pattern) {
    return py_to<rc<list<str>>>(_glob_mod.glob(pattern));
}

int main(int argc, char** argv) {
    pytra_configure_from_argv(argc, argv);
    return 0;
}

#include "core/py_runtime.h"
#include "core/process_runtime.h"

/* pytra.std.os_path: extern-marked os.path subset with Python runtime fallback. */

str join(const str& a, const str& b) {
    return os.path.join(a, b);
}

str dirname(const str& p) {
    return os.path.dirname(p);
}

str basename(const str& p) {
    return os.path.basename(p);
}

::std::tuple<str, str> splitext(const str& p) {
    return os.path.splitext(p);
}

str abspath(const str& p) {
    return os.path.abspath(p);
}

bool exists(const str& p) {
    return os.path.exists(p);
}

int main(int argc, char** argv) {
    pytra_configure_from_argv(argc, argv);
    return 0;
}

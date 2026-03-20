#include "core/py_runtime.h"
#include "core/process_runtime.h"
#include "built_in/io_ops.h"

/* Extern-marked I/O helper built-ins. */

void py_print(const object& value) {
    py_print(value);
}

int main(int argc, char** argv) {
    pytra_configure_from_argv(argc, argv);
    return 0;
}

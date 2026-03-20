#include "core/py_runtime.h"
#include "core/process_runtime.h"

/* pytra.std.time: extern-marked time API with Python runtime fallback. */

float64 perf_counter() {
    return time.perf_counter();
}

int main(int argc, char** argv) {
    pytra_configure_from_argv(argc, argv);
    return 0;
}

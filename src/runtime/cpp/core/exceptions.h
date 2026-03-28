#ifndef PYTRA_BUILT_IN_EXCEPTIONS_H
#define PYTRA_BUILT_IN_EXCEPTIONS_H

#include <stdexcept>
#include <string>

struct SystemExit {
    int code;

    explicit SystemExit(int exit_code)
        : code(exit_code) {}
};

#endif  // PYTRA_BUILT_IN_EXCEPTIONS_H

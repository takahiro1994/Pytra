#ifndef PYTRA_STD_SYS_H
#define PYTRA_STD_SYS_H

#include "core/py_runtime.h"

extern list<str> argv;
extern list<str> path;

void exit(int64 code = 0);
void set_argv(const list<str>& values);
void set_path(const list<str>& values);
void write_stderr(const str& text);
void write_stdout(const str& text);

#endif  // PYTRA_STD_SYS_H

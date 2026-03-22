// AUTO-GENERATED FILE. DO NOT EDIT.
// source: src/pytra/built_in/scalar_ops.py
// generated-by: tools/gen_runtime_from_manifest.py

using System;
using System.Collections.Generic;
using System.Linq;
using Any = System.Object;
using int64 = System.Int64;
using float64 = System.Double;
using str = System.String;

namespace Pytra.CsModule
{
    public static class scalar_ops_helper
    {
        public static long py_to_int64_base(string v, long py_base)
        {
            return py_int(v, py_base);
        }

        public static long py_ord(string ch)
        {
            return Pytra.CsModule.py_runtime.py_ord(ch);
        }

        public static string py_chr(long codepoint)
        {
            return System.Convert.ToString(System.Convert.ToChar(System.Convert.ToInt32(codepoint)));
        }

    }
}

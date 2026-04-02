"""EAST3 -> Scala source emitter.

Initial scaffold for the toolchain2 Scala backend.
This file intentionally supports only a narrow bootstrap subset so the
backend can be wired incrementally under `docs/ja/todo/java.md`.
"""

from __future__ import annotations

from pathlib import Path

from pytra.std.json import JsonVal

from toolchain2.emit.common.code_emitter import RuntimeMapping, load_runtime_mapping
from toolchain2.emit.common.common_renderer import CommonRenderer
from toolchain2.emit.scala.types import _safe_scala_ident
from toolchain2.emit.scala.types import scala_type


class ScalaRenderer(CommonRenderer):
    def __init__(self, mapping: RuntimeMapping) -> None:
        super().__init__("scala")
        self.mapping = mapping

    def render_module(self, east3_doc: dict[str, JsonVal]) -> str:
        module_id = self._str(east3_doc, "module_id")
        if module_id == "":
            meta = east3_doc.get("meta")
            if isinstance(meta, dict):
                module_id = self._str(meta, "module_id")
        object_name = _safe_scala_ident(module_id.replace(".", "_") if module_id != "" else "Main")
        self._emit("import scala.collection.mutable")
        self._emit_blank()
        self._emit("object " + object_name + " {")
        self.state.indent_level += 1
        body = self._list(east3_doc, "body")
        if len(body) == 0:
            self._emit("// bootstrap scaffold")
        else:
            for stmt in body:
                self._emit_stmt(stmt)
        self.state.indent_level -= 1
        self._emit("}")
        return self.finish()

    def _emit_stmt(self, node: JsonVal) -> None:
        if not isinstance(node, dict):
            raise RuntimeError("scala emitter: stmt node must be dict")
        kind = self._str(node, "kind")
        if kind == "Pass":
            self._emit("()")
            return
        if kind == "AnnAssign":
            target = node.get("target")
            target_name = _safe_scala_ident(self._str(target, "id"))
            decl_type = self._str(node, "decl_type")
            value = self._emit_expr(node.get("value"))
            self._emit("val " + target_name + ": " + scala_type(decl_type) + " = " + value)
            return
        if kind == "Assign":
            target = node.get("target")
            target_name = _safe_scala_ident(self._str(target, "id"))
            value = self._emit_expr(node.get("value"))
            self._emit("var " + target_name + " = " + value)
            return
        if kind == "Expr":
            self._emit(self._emit_expr(node.get("value")))
            return
        raise RuntimeError("scala emitter: unsupported stmt kind: " + kind)

    def _emit_expr(self, node: JsonVal) -> str:
        if not isinstance(node, dict):
            return "null"
        kind = self._str(node, "kind")
        if kind == "Constant":
            value = node.get("value")
            if value is None:
                return "null"
            if isinstance(value, bool):
                return "true" if value else "false"
            if isinstance(value, int) and not isinstance(value, bool):
                return str(value) + "L"
            if isinstance(value, float):
                return repr(value)
            if isinstance(value, str):
                return self._quote_string(value)
        if kind == "Name":
            return _safe_scala_ident(self._str(node, "id"))
        if kind == "List":
            elems = [self._emit_expr(elem) for elem in self._list(node, "elements")]
            return "mutable.ArrayBuffer(" + ", ".join(elems) + ")"
        raise RuntimeError("scala emitter: unsupported expr kind: " + kind)


def emit_scala_module(east3_doc: dict[str, JsonVal]) -> str:
    mapping_path = Path(__file__).resolve().parents[3] / "runtime" / "scala" / "mapping.json"
    renderer = ScalaRenderer(load_runtime_mapping(mapping_path))
    return renderer.render_module(east3_doc)


__all__ = ["emit_scala_module"]

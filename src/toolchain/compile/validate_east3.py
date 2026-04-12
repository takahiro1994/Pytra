"""EAST3 invariant validator.

spec-agent / P0-OBJECT-ZERO:
- resolved_type: "object" is forbidden in EAST3.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from pytra.std.json import JsonVal
from toolchain.compile.jv import Node


@dataclass
class ValidationResult:
    source_path: str = ""
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    stats: dict[str, int] = field(default_factory=dict)

    @property
    def ok(self) -> bool:
        return len(self.errors) == 0


def validate_east3(doc: Node) -> ValidationResult:
    result = ValidationResult()
    sp = doc.get("source_path")
    result.source_path = str(sp) if isinstance(sp, str) else ""

    stage = doc.get("east_stage")
    if stage != 3:
        result.errors.append("east_stage is " + str(stage) + ", expected 3")

    sv = doc.get("schema_version")
    if sv != 1:
        result.errors.append("schema_version is " + str(sv) + ", expected 1")

    counts = {"object_resolved_type": 0}
    _walk(doc, "$", result, counts)
    result.stats.update(counts)
    return result


def _walk(node: JsonVal, path: str, result: ValidationResult, counts: dict[str, int]) -> None:
    if isinstance(node, list):
        for i, item in enumerate(node):
            _walk(item, path + "[" + str(i) + "]", result, counts)
        return

    if not isinstance(node, dict):
        return

    rt = node.get("resolved_type")
    if isinstance(rt, str) and rt == "object":
        counts["object_resolved_type"] += 1
        kind = node.get("kind")
        kind_str = str(kind) if isinstance(kind, str) else "<dict>"
        result.errors.append(path + ": " + kind_str + ' resolved_type is forbidden "object"')

    for k, v in node.items():
        if k == "source_span":
            continue
        _walk(v, path + "." + k, result, counts)


def format_result(result: ValidationResult) -> str:
    lines: list[str] = []
    status = "PASS" if result.ok else "FAIL"
    lines.append(status + ": " + result.source_path)
    for err in result.errors:
        lines.append("  ERROR: " + err)
    count = result.stats.get("object_resolved_type", 0)
    lines.append("  object_resolved_type: " + str(count))
    return "\n".join(lines)

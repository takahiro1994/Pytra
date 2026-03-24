"""EAST3 ForCore TupleTarget expansion pass.

Converts ForCore nodes with TupleTarget into a single NameTarget with
element assignments inserted at the beginning of the loop body.

Before:
    ForCore(target_plan=TupleTarget([NameTarget("i"), NameTarget("v")]),
            body=[...])

After:
    ForCore(target_plan=NameTarget("__iter_tmp_1"),
            body=[Assign(i, Subscript(__iter_tmp_1, 0)),
                  Assign(v, Subscript(__iter_tmp_1, 1)),
                  ...])
"""

from __future__ import annotations

from typing import Any


_tmp_counter: list[int] = [0]


def _next_tmp() -> str:
    _tmp_counter[0] += 1
    return "__iter_tmp_" + str(_tmp_counter[0])


def _make_subscript(owner_name: str, index: int, elem_type: str) -> dict[str, Any]:
    """Create a Subscript node: owner[index]."""
    return {
        "kind": "Subscript",
        "value": {
            "kind": "Name",
            "id": owner_name,
            "resolved_type": "tuple",
        },
        "slice": {
            "kind": "Constant",
            "value": index,
            "resolved_type": "int64",
        },
        "resolved_type": elem_type if elem_type != "" else "object",
    }


def _expand_forcore_tuple_target(node: Any) -> None:
    """Walk EAST3 and expand ForCore TupleTarget nodes."""
    if isinstance(node, list):
        for item in node:
            _expand_forcore_tuple_target(item)
        return
    if not isinstance(node, dict):
        return
    nd: dict[str, Any] = node

    if nd.get("kind") == "ForCore":
        target_plan = nd.get("target_plan")
        if isinstance(target_plan, dict) and target_plan.get("kind") == "TupleTarget":
            elements = target_plan.get("elements")
            if isinstance(elements, list) and len(elements) >= 2:
                # Generate temp variable name
                tmp_name = _next_tmp()

                # Collect element names and types
                elem_assigns: list[dict[str, Any]] = []
                for i, elem in enumerate(elements):
                    if not isinstance(elem, dict):
                        continue
                    if elem.get("kind") != "NameTarget":
                        continue
                    elem_name = elem.get("id", "")
                    elem_type = elem.get("target_type", "")
                    if not isinstance(elem_name, str) or elem_name == "":
                        continue
                    if not isinstance(elem_type, str):
                        elem_type = ""
                    # Create: elem_name = __iter_tmp[i]
                    assign: dict[str, Any] = {
                        "kind": "Assign",
                        "target": {
                            "kind": "Name",
                            "id": elem_name,
                            "resolved_type": elem_type if elem_type != "" else "object",
                        },
                        "value": _make_subscript(tmp_name, i, elem_type),
                        "decl_type": elem_type if elem_type != "" else "unknown",
                        "declare": True,
                    }
                    elem_assigns.append(assign)

                # Replace TupleTarget with NameTarget
                # Preserve direct_unpack_names for emitters that prefer it
                direct_names = [
                    elem.get("id", "") for elem in elements
                    if isinstance(elem, dict) and elem.get("kind") == "NameTarget"
                ]
                nd["target_plan"] = {
                    "kind": "NameTarget",
                    "id": tmp_name,
                    "target_type": target_plan.get("target_type", ""),
                    "direct_unpack_names": direct_names,
                    "tuple_expanded": True,
                }

                # Prepend element assignments to body
                body = nd.get("body")
                if isinstance(body, list):
                    nd["body"] = elem_assigns + body

    # Recurse into all children
    for value in nd.values():
        if isinstance(value, (dict, list)):
            _expand_forcore_tuple_target(value)


def expand_forcore_tuple_targets(module: dict[str, Any]) -> dict[str, Any]:
    """Top-level entry: expand ForCore TupleTarget nodes.

    Mutates *module* in place and returns it.
    """
    _tmp_counter[0] = 0
    _expand_forcore_tuple_target(module)
    return module

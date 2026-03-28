from pytra.std import json


if __name__ == "__main__":
    doc = json.loads_obj('{"a": 1, "b": [2, 3]}')
    if doc is not None:
        print(json.dumps(doc.raw, indent=2))

from pytra.std import json


if __name__ == "__main__":
    value = json.loads('"\\u3042"')
    if value is not None:
        print(value.as_str())

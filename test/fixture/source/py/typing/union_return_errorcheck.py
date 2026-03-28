def parse_int(s: str) -> int:
    if not s.isdigit():
        raise ValueError("bad")
    return int(s)


def process(s: str) -> int:
    value = parse_int(s)
    return value


if __name__ == "__main__":
    try:
        x = process("7")
        print(x)
        y = process("x")
        print(y)
    except ValueError as err:
        print(err)

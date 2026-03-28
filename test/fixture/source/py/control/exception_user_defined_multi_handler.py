class ParseError(ValueError):
    line: int

    def __init__(self, line: int, msg: str) -> None:
        super().__init__(msg)
        self.line = line


def fail(mode: int) -> None:
    if mode == 1:
        raise ParseError(7, "bad")
    raise TypeError("oops")


def run_case(mode: int) -> None:
    try:
        fail(mode)
    except ParseError as err:
        print("parse", err.line, str(err))
    except TypeError as err:
        print("type", str(err))
    finally:
        print("done", mode)


if __name__ == "__main__":
    run_case(1)
    run_case(2)

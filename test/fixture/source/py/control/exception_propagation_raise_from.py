def leaf() -> None:
    raise ValueError("boom")


def middle() -> None:
    try:
        leaf()
    except ValueError as exc:
        raise RuntimeError("wrapped") from exc


def outer() -> None:
    middle()


if __name__ == "__main__":
    try:
        outer()
    except RuntimeError as err:
        print(err)

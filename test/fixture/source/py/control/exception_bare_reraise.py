def leaf() -> None:
    raise ValueError("boom")


if __name__ == "__main__":
    try:
        try:
            leaf()
        except ValueError:
            raise
    except ValueError as err:
        print(err)

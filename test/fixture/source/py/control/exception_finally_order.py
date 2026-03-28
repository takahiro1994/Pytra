def leaf() -> None:
    raise ValueError("boom")


if __name__ == "__main__":
    try:
        leaf()
    finally:
        print("cleanup")

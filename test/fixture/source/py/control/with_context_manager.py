from pytra.utils.assertions import py_assert_all, py_assert_eq


class TrackingContext:
    def __init__(self) -> None:
        self.log: list[str] = []

    def __enter__(self) -> "TrackingContext":
        self.log.append("enter")
        return self

    def __exit__(self, exc_type: object, exc_val: object, exc_tb: object) -> None:
        self.log.append("exit")


def run_with_context_manager() -> bool:
    checks: list[bool] = []

    # basic: __enter__ and __exit__ are called in order
    ctx = TrackingContext()
    with ctx as c:
        c.log.append("body")
    checks.append(py_assert_eq(ctx.log, ["enter", "body", "exit"], "basic_order"))

    # __exit__ is called even when exception is raised
    ctx2 = TrackingContext()
    try:
        with ctx2 as c2:
            c2.log.append("body")
            raise ValueError("boom")
    except ValueError:
        pass
    checks.append(py_assert_eq(ctx2.log, ["enter", "body", "exit"], "exception_safety"))

    # __enter__ return value is bound to as-variable
    ctx3 = TrackingContext()
    with ctx3 as c3:
        checks.append(py_assert_eq(c3 is ctx3, True, "enter_returns_self"))

    return py_assert_all(checks, "with_context_manager")


if __name__ == "__main__":
    print(run_with_context_manager())

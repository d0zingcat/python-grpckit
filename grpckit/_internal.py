class _Missing:
    """None type which differs from Python None."""

    def __repr__(self) -> str:
        return "no value"

    def __reduce__(self) -> str:
        return "_missing"

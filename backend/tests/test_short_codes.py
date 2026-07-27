import pytest

from app.utils.base62 import encode_base62


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        (0, "0"),
        (9, "9"),
        (10, "a"),
        (35, "z"),
        (36, "A"),
        (61, "Z"),
        (62, "10"),
    ],
)
def test_encode_base62_known_values(value: int, expected: str) -> None:
    assert encode_base62(value) == expected


def test_encode_base62_rejects_negative_values() -> None:
    with pytest.raises(ValueError):
        encode_base62(-1)
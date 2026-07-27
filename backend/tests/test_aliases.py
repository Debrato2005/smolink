import pytest

from app.utils.aliases import normalize_alias


@pytest.mark.parametrize("alias", ["abc", "my-link", "a" * 64])
def test_normalize_alias_accepts_valid_aliases(alias: str) -> None:
    assert normalize_alias(alias) == alias


def test_normalize_alias_lowercases_input() -> None:
    assert normalize_alias("My-Link") == "my-link"


@pytest.mark.parametrize(
    "alias",
    ["ab", "a" * 65, "bad alias", "bad_alias", "api", "health"],
)
def test_normalize_alias_rejects_invalid_or_reserved_aliases(
    alias: str,
) -> None:
    with pytest.raises(ValueError):
        normalize_alias(alias)
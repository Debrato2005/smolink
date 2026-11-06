import re

class InvalidAliasError(ValueError):
    pass

ALIAS_PATTERN = re.compile(r"^[a-z0-9-]{3,64}$")
RESERVED_ALIASES = frozenset(
    {
        "admin",
        "api",
        "assets",
        "auth",
        "dashboard",
        "docs",
        "forgot-password",
        "health",
        "login",
        "me",
        "openapi.json",
        "redoc",
        "register",
        "reset-password",
        "settings",
        "static",
        "urls",
        "verify-email",
    }
)


def normalize_alias(alias: str) -> str:
    normalized = alias.lower()

    if normalized in RESERVED_ALIASES:
        raise InvalidAliasError("Alias is reserved")

    if not ALIAS_PATTERN.fullmatch(normalized):
        raise InvalidAliasError(
            "Alias must contain 3-64 lowercase letters, numbers, or hyphens"
        )

    return normalized